import { default as dac4D_component } from './dac4D_data.svelte'
import { default as dac16D_component } from './dac16D.svelte'
import { dac4D } from './dac4D'
import { dac16D } from './dac16D_data'
import type { IModule } from '../../state/systemState.svelte'
import { SvelteComponent } from 'svelte'
import type { CoreModule } from '../../state/systemState.svelte'
import type { SystemState, JsonSystemState } from '../../state/systemState.svelte'
// import { writable } from 'svelte';
import type { ComponentType } from 'svelte';

// interface Components {
//   dac4D: ComponentType;
//   dac16D: ComponentType;
// }

const components: any = {
    dac4D_component, 
    dac16D_component, 
}

type Constructor<T> = new(data: IModule) => T;

interface ModulesDict {
    [key: string]: Constructor<IModule>;
}

const modules: ModulesDict = {
    dac4D,
    dac16D,
}


function getComponent(name: any): ComponentType {
    const component = components[name];
    if (!component) {
      throw new Error(`Component ${name} does not exist`);
    }
    return component;
  }


function createComponentArray(system_state: SystemState): any {
    return system_state.data.map((module) => {
        const component = getComponent(module.core.type)
        return component
    })
}

export function createSystemStateFromJson(parsed: JsonSystemState): SystemState {
  const data = parsed.data.map((item: any) => {
    // depending on the type of module, we need dynamically create the module objects
    const module = new modules[item.core.type](item);
    return module as IModule
  });
  return {data, valid: parsed.valid, dev_mode: parsed.dev_mode };
}



// I need to make the TotalState.data as an object and find a way to connect the data of that object to the component. 