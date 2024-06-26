import { default as dac4D_component } from "./dac4D.svelte";
import { dac4D } from "./dac4D_data.svelte";

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
// import { writable } from 'svelte';
import type { ComponentType } from "svelte";

import { system_state } from "../../state/systemState.svelte";
import type { JsonModule } from "../../state/systemState.svelte";
// import type { Updater } from '../../state/systemState.svelte'

// interface Components {
//   dac4D: ComponentType;
//   dac16D: ComponentType;
// }

const components: any = {
  dac4D: dac4D_component,
  // dac4D_old: dac4D_old_component,
  dac16D: dac16D_component,
};

const modules: ModulesDict = {
  empty,
  dac4D,
  // dac4D_old,
  dac16D,
};

// interface IModuleUpdater extends IModule, Updater {}

type Constructor<T> = new (data: JsonModule) => T;

interface ModulesDict {
  [key: string]: Constructor<IModule>;
}

export class ComponentManager {
  public component_array: Array<any> = $state([]);
  public module_idx: number[] = $state([]);

  constructor() {
    this.component_array = [];
  }

  public createComponentArray(module_list: IModule[]): any {

    while(this.component_array.length > 0) {
      this.component_array.pop();
    }

    console.log("creating component array");
    // const components = [];
    for (const module of module_list) {
      if (module.core.type !== "empty") {
        const component = getComponent(module.core.type);
        this.component_array.push(component);
      }
    }
    // this.component_array = components;
  }

  public updateModuleIdx(num_modules: number) {

    while(this.module_idx.length > 0) {
      this.module_idx.pop();
    }

    for (let i = 0; i < num_modules; i++) {
      if (system_state.data[i].core.type !== "empty") {
        this.module_idx.push(i);
      }
    }
  }
}

export let manager = new ComponentManager();

function getComponent(name: any): ComponentType {
  // console.log("the name is: ", name)
  const component = components[name];
  // console.log("the name of the component is: ", component)
  if (!component) {
    throw new Error(`Component ${name} does not exist`);
  }
  return component;
}

export function createSystemStatefromJson(parsed: JsonSystemState) {
  const data = parsed.data.map((item: JsonModule) => {
    // depending on the type of module, we need dynamically create the module objects
    console.log("the type of the module is: ", item.core.type);
    const module = new modules[item.core.type](item);
    return module as IModule;
  });
  data.forEach((item) => system_state.data.push(item));
  system_state.valid = parsed.valid;
  system_state.dev_mode = parsed.dev_mode;

  manager.createComponentArray(system_state.data);
  manager.updateModuleIdx(system_state.data.length);
}

export function updateSystemStatefromJson(parsed: JsonSystemState) {
  let j = 0
  for (let i = 0; i < parsed.data.length; i++) {
    if (parsed.data[i].core.type !== system_state.data[i].core.type) {
      console.log("DEVIATION FOUND")
      j = j + 1
      system_state.data[i] = new modules[parsed.data[i].core.type](
        parsed.data[i]
      );
    } else {
      system_state.data[i].update(parsed.data[i]);
    }
  }
  system_state.valid = parsed.valid;
  system_state.dev_mode = parsed.dev_mode;

  if (j>0) {
    console.log("something changed, updating the component array")
    console.log("something changed, updating the component array")
    console.log("something changed, updating the component array")
    manager.createComponentArray(system_state.data);
    manager.updateModuleIdx(system_state.data.length);
  }
}

export function updateSystemStatetoFallback() {
  const module_0: dac4D = new dac4D({
    core: { slot: 0, type: "dac4D", name: "my 4ch module 1" },
  });
  const module_1: empty = new empty({
    core: { slot: 1, type: "empty", name: "empty" },
  });
  const module_2: dac16D = new dac16D({
    core: { slot: 2, type: "dac16D", name: "my 16ch module 1" },
  });
  const module_3: dac16D = new dac16D({
    core: { slot: 3, type: "dac16D", name: "my 16ch module" },
  });
  const module_4: empty = new empty({
    core: { slot: 4, type: "empty", name: "empty" },
  });
  const module_5: dac16D = new dac16D({
    core: { slot: 5, type: "dac16D", name: "my 16ch module" },
  });
  const module_6: empty = new empty({
    core: { slot: 6, type: "empty", name: "empty" },
  });
  const module_7: empty = new empty({
    core: { slot: 7, type: "empty", name: "empty" },
  });
  system_state.data = [
    module_0,
    module_1,
    module_2,
    module_3,
    module_4,
    module_5,
    module_6,
    module_7,
  ];
  system_state.valid = false;
  system_state.dev_mode = true;

  manager.createComponentArray(system_state.data);
  manager.updateModuleIdx(system_state.data.length);
}

// I need to make the TotalState.data as an object and find a way to connect the data of that object to the component.
