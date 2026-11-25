import { default as dac4D_component } from "./dac4D.svelte";
import { dac4D } from "./dac4D_data.svelte";

import { default as adc4D_component } from "./adc4D.svelte";
import { adc4D } from "./adc4D_data.svelte";

import { empty } from "./empty_data.svelte";

// import { default as dac4D_old_component } from '../depreciated/dac4D_old.svelte'
// import { dac4D_old } from '../depreciated/dac4D_old_data.svelte'

import { default as dac16D_component } from "./dac16D.svelte";
import { dac16D } from "./dac16D_data.svelte";

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


interface ModuleProps {
  module_index: number;
}

const components: any = {
  dac4D: dac4D_component,
  adc4D: adc4D_component,
  dac16D: dac16D_component,
};

// Make ComponentHolder generic to accept props type with proper constraint
interface ComponentHolder<P extends Record<string, any> = {}> {
  name: string;
  component: Component<P>;
  module_index: number;
}


interface ComponentCollection {
  [key: string]: ComponentHolder<ModuleProps>;
}

// Now the constant is properly typed with the required props
const cc: ComponentCollection = {
  dac4D: {
    name: "dac4D",
    component: dac4D_component,
    module_index: 0,
  },
  adc4D: {
    name: "adc4D",
    component: adc4D_component,
    module_index: 0,
  },
  dac16D: {
    name: "dac16D",
    component: dac16D_component,
    module_index: 0,
  }
};


const modules: ModulesDict = {
  empty,
  dac4D,
  adc4D,
  // dac4D_old,
  dac16D,
};

// interface IModuleUpdater extends IModule, Updater {}

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
