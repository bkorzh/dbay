

import { default as dac4D_component } from './dac4D.svelte'
import { dac4D } from './dac4D_data.svelte'

import { empty } from './empty_data.svelte'

// import { default as dac4D_old_component } from '../depreciated/dac4D_old.svelte'
// import { dac4D_old } from '../depreciated/dac4D_old_data.svelte'

import { default as dac16D_component } from './dac16D.svelte'
import { dac16D } from './dac16D_data.svelte'




import type { IModule } from '../../state/systemState.svelte'
// import { SvelteComponent } from 'svelte'
import type { CoreModule } from '../../state/systemState.svelte'
import type { SystemState, JsonSystemState } from '../../state/systemState.svelte'
// import { writable } from 'svelte';
import type { ComponentType } from 'svelte';

import { system_state } from '../../state/systemState.svelte'

// interface Components {
//   dac4D: ComponentType;
//   dac16D: ComponentType;
// }

const components: any = {
    dac4D: dac4D_component, 
    // dac4D_old: dac4D_old_component,
    dac16D: dac16D_component, 
}

const modules: ModulesDict = {
  empty,
  dac4D,
  // dac4D_old,
  dac16D,
}

type Constructor<T> = new(data: IModule) => T;

interface ModulesDict {
    [key: string]: Constructor<IModule>;
}




function getComponent(name: any): ComponentType {
    // console.log("the name is: ", name)
    const component = components[name];
    // console.log("the name of the component is: ", component)
    if (!component) {
      throw new Error(`Component ${name} does not exist`);
    }
    return component;
  }


export function createComponentArray(module_list: IModule[]): any {
    const components = [];
    for (const module of module_list) {
        if (module.core.type !== "empty") {
            const component = getComponent(module.core.type);
            components.push(component);
        }
    }
    return components;
}


export function updateSystemStatefromJson(parsed: JsonSystemState) {
  const data = parsed.data.map((item: any) => {
    // depending on the type of module, we need dynamically create the module objects
    const module = new modules[item.core.type](item);
    return module as IModule
  });
  system_state.data = data;
  system_state.valid = parsed.valid;
  system_state.dev_mode = parsed.dev_mode;
}

export function updateSystemStatetoFallback() {
  const module_0: dac4D = new dac4D({core: {slot: 0, type: "dac4D", name: "my 4ch module 1"}});
  const module_1: empty = new empty({core: {slot: 1, type: "empty", name: "empty"}});
  const module_2: dac16D = new dac16D({core: {slot: 2, type: "dac16D", name: "my 16ch module 1"}});
  const module_3: dac16D = new dac16D({core: {slot: 3, type: "dac16D", name: "my 16ch module"}});
  const module_4: empty = new empty({core: {slot: 4, type: "empty", name: "empty"}});
  const module_5: dac16D = new dac16D({core: {slot: 5, type: "dac16D", name: "my 16ch module"}});
  const module_6: empty = new empty({core: {slot: 6, type: "empty", name: "empty"}});
  const module_7: empty = new empty({core: {slot: 7, type: "empty", name: "empty"}});
  system_state.data = [module_0, module_1, module_2, module_3, module_4, module_5, module_6, module_7];
  system_state.valid = false;
  system_state.dev_mode = true;
}



// I need to make the TotalState.data as an object and find a way to connect the data of that object to the component. 