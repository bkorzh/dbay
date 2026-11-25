import { default as dac4D_component } from "./dac4D.svelte";
import { dac4D } from "./dac4D_data.svelte";

import { default as adc4D_component } from "./adc4D.svelte";
import { adc4D } from "./adc4D_data.svelte";

import { empty } from "./empty_data.svelte";

// import { default as dac4D_old_component } from '../depreciated/dac4D_old.svelte'
// import { dac4D_old } from '../depreciated/dac4D_old_data.svelte'

import { default as dac16D_component } from "./dac16D.svelte";
import { dac16D } from "./dac16D_data.svelte";

// demoD is the worked example from the Adding a Module guide, not real hardware.
import { default as demoD_component } from "./demoD.svelte";
import { demoD } from "./demoD_data.svelte";

import type { IModule } from "../../state/systemState.svelte";
// import { SvelteComponent } from 'svelte'
import type { CoreModule } from "../../state/systemState.svelte";
import type {
  SystemState,
  JsonSystemState,
} from "../../state/systemState.svelte";
import type { Component } from "svelte";

import { system_state } from "../../state/systemState.svelte";
import type { JsonModule } from "../../state/systemState.svelte";
import { syncRuntime } from "../../sync/runtime.svelte";
import { joinJsonPointer } from "lab-link/core";
import { MODULE_CATALOG, moduleCatalogEntry } from "./module_catalog";


interface ModuleProps {
  module_index: number;
}

// Make ComponentHolder generic to accept props type with proper constraint
interface ComponentHolder<P extends Record<string, any> = {}> {
  name: string;
  component: Component<P>;
  module_index: number;
}


interface ComponentCollection {
  [key: string]: ComponentHolder<ModuleProps>;
}

type ReplaceModule = (data: JsonModule) => void;
type Constructor<T> = new (
  data: any,
  path: string,
  parsed: JsonModule,
  replaceSelf?: ReplaceModule,
) => T;

interface ModulesDict {
  [key: string]: Constructor<IModule>;
}

/**
 * The code bound to each module type: the class that mirrors its state, and the
 * component that draws it. Presentation (title, icon, adder blurb) lives in
 * `module_catalog.ts`; these two lists must cover the same types, which
 * `assertRegistryMatchesCatalog` and `module_registry.test.ts` enforce.
 *
 * A type with no component is never drawn — `empty` is the only one.
 */
export interface ModuleBinding {
  data: Constructor<IModule>;
  component?: Component<ModuleProps>;
}

export const MODULE_BINDINGS: Record<string, ModuleBinding> = {
  empty: { data: empty },
  dac4D: { data: dac4D, component: dac4D_component },
  adc4D: { data: adc4D, component: adc4D_component },
  dac16D: { data: dac16D, component: dac16D_component },
  // demoD is the worked example from the Adding a Module guide, not real hardware.
  demoD: { data: demoD, component: demoD_component },
};

/**
 * Fails loudly when the catalog and the bindings disagree — the drift this
 * split is meant to prevent. Called at module load so a mistake shows up the
 * first time the app runs, not when a user picks the broken entry.
 */
export function assertRegistryMatchesCatalog(): string[] {
  const problems: string[] = [];
  const bound = new Set(Object.keys(MODULE_BINDINGS));

  for (const entry of MODULE_CATALOG) {
    if (!bound.has(entry.type)) {
      problems.push(
        `"${entry.type}" is in module_catalog.ts but has no entry in MODULE_BINDINGS, ` +
          `so the app cannot construct or draw it.`,
      );
      continue;
    }
    if (entry.addable !== false && !MODULE_BINDINGS[entry.type].component) {
      problems.push(
        `"${entry.type}" can be added to a slot but has no component to draw it.`,
      );
    }
  }

  for (const type of bound) {
    if (!moduleCatalogEntry(type)) {
      problems.push(
        `"${type}" is in MODULE_BINDINGS but missing from module_catalog.ts, ` +
          `so it has no title, icon, or entry in the module adder.`,
      );
    }
  }

  return problems;
}

for (const problem of assertRegistryMatchesCatalog()) {
  console.error(`[module registry] ${problem}`);
}

// Derived from the two lists above, so adding a module never means editing these.
const modules: ModulesDict = Object.fromEntries(
  Object.entries(MODULE_BINDINGS).map(([type, binding]) => [type, binding.data]),
);

const cc: ComponentCollection = Object.fromEntries(
  Object.entries(MODULE_BINDINGS)
    .filter(([, binding]) => binding.component)
    .map(([type, binding]) => [
      type,
      { name: type, component: binding.component!, module_index: 0 },
    ]),
);

export class ComponentManager {
  public component_array: Array<ComponentHolder<ModuleProps>> = $state([]);
  // public module_idx: number[] = $state([]);

  constructor() {
    this.component_array = [];
  }

  public createComponentArray(module_list: IModule[]): any {

    // not deleting and recreating the array because its a $state() object
    while (this.component_array.length > 0) {
      this.component_array.pop();
    }

    for (const module of module_list) {
      if (module.core.type !== "empty") {
        const component_holder = getComponentHolder(module.core.type);
        component_holder.module_index = module.core.slot;
        this.component_array.push(component_holder);
      }
    }
    this.component_array.sort((a, b) => a.module_index - b.module_index);
  }
}

export let manager = new ComponentManager();

function getComponentHolder(name: any): ComponentHolder<ModuleProps> {
  const component_holder_reference = cc[name];
  const component_holder = { ...component_holder_reference };
  if (!component_holder) {
    throw new Error(`Component ${name} does not exist`);
  }
  return component_holder;
}

function modulePath(slot: number): string {
  return joinJsonPointer("", "data", String(slot));
}

function createModule(item: JsonModule): IModule {
  const slot = item.core.slot;
  return new modules[item.core.type](
    syncRuntime,
    modulePath(slot),
    item,
    (next: JsonModule) => replaceModule(slot, next),
  ) as IModule;
}

function replaceModule(slot: number, next: JsonModule): void {
  system_state.data[slot]?.dispose?.();
  system_state.data[slot] = createModule(next);
  manager.createComponentArray(system_state.data);
}

export function createSystemStatefromJson(parsed: JsonSystemState) {
  const data = parsed.data.map((item: JsonModule) => {
    // depending on the type of module, we need dynamically create the module objects
    return createModule(item);
  });
  system_state.data.forEach((item) => item.dispose?.());
  while (system_state.data.length > 0) {
    system_state.data.pop();
  }
  data.forEach((item) => system_state.data.push(item));
  system_state.valid = parsed.valid;
  system_state.dev_mode = parsed.dev_mode;

  manager.createComponentArray(system_state.data);
  // manager.updateModuleIdx(system_state.data.length);
}

export function updateSystemStatefromJson(parsed: JsonSystemState) {
  let j = 0
  for (let i = 0; i < parsed.data.length; i++) {
    if (parsed.data[i].core.type !== system_state.data[i].core.type) {
      // console.log("DEVIATION FOUND")

      // deviation found bewteen state stored in browser and state from server
      j = j + 1
      system_state.data[i]?.dispose?.();
      system_state.data[i] = createModule(parsed.data[i]);
    } else {
      system_state.data[i].update(parsed.data[i]);
    }
  }
  system_state.valid = parsed.valid;
  system_state.dev_mode = parsed.dev_mode;

  if (j > 0) {
    // console.log("something changed, updating the component array")

    manager.createComponentArray(system_state.data);
    // manager.updateModuleIdx(system_state.data.length);
  }
}

export function updateSystemStatetoFallback() {
  const fallbackState: JsonSystemState = {
    data: [
      { core: { slot: 0, type: "dac4D", name: "my 4ch module 1" } },
      { core: { slot: 1, type: "adc4D", name: "my 4ch ADC module" } },
      { core: { slot: 2, type: "dac16D", name: "my 16ch module 1" } },
      { core: { slot: 3, type: "dac16D", name: "my 16ch module" } },
      { core: { slot: 4, type: "empty", name: "empty" } },
      { core: { slot: 5, type: "dac16D", name: "my 16ch module" } },
      { core: { slot: 6, type: "empty", name: "empty" } },
      { core: { slot: 7, type: "empty", name: "empty" } },
    ],
    valid: false,
    dev_mode: true,
  };

  system_state.data.forEach((item) => item.dispose?.());
  system_state.data = fallbackState.data.map((item) => createModule(item));
  system_state.valid = fallbackState.valid;
  system_state.dev_mode = fallbackState.dev_mode;

  manager.createComponentArray(system_state.data);
  // manager.updateModuleIdx(system_state.data.length);
}

// I need to make the TotalState.data as an object and find a way to connect the data of that object to the component.
