import { default as dac4D_component } from './dac4D.svelte'
import { default as dac16D_component } from './dac16D.svelte'
import { dac4D } from './dac4D_data.svelte'
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
    dac16D: dac16D_component, 
}

const modules: ModulesDict = {
  dac4D,
  dac16D,
}

type Constructor<T> = new(data: IModule) => T;

interface ModulesDict {
    [key: string]: Constructor<IModule>;
}




function getComponent(name: any): ComponentType {
    console.log("the name is: ", name)
    console.log("the components are: ", components)
    const component = components[name];
    if (!component) {
      throw new Error(`Component ${name} does not exist`);
    }
    return component;
  }


export function createComponentArray(module_list: IModule[]): any {
    return module_list.map((module) => {
        const component = getComponent(module.core.type)
        return component
    })
}

// export function createSystemStateFromJson(parsed: JsonSystemState): IModule[] {
//   const data = parsed.data.map((item: any) => {
//     // depending on the type of module, we need dynamically create the module objects
//     const module = new modules[item.core.type](item);
//     return module as IModule
//   });
//   return data
// }

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
  const module_1: dac4D = new dac4D({core: {slot: 1, type: "dac4D", name: "my 4ch module 1"}});
  const module_2: dac4D = new dac4D({core: {slot: 1, type: "dac4D", name: "my 4ch module 1"}});
  const module_3: dac16D = new dac16D({core: {slot: 1, type: "dac4D", name: "my 4ch module 1"}});
  system_state.data = [module_1, module_2, module_3];
  system_state.valid = false;
  system_state.dev_mode = true;
}



// I need to make the TotalState.data as an object and find a way to connect the data of that object to the component. 