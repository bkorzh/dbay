import { default as dac4D } from './dac4D.svelte'
import { default as dac16D } from './dac16D.svelte'
import { SvelteComponent } from 'svelte'
import type { SystemState } from '../../state/systemState'
// import { writable } from 'svelte';
import type { ComponentType } from 'svelte';

// interface Components {
//   dac4D: ComponentType;
//   dac16D: ComponentType;
// }

const components: any = {
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
        const component = getComponent(module.module.type)
        return component
    })
}



// I need to make the TotalState.data as an object and find a way to connect the data of that object to the component. 