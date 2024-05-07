import { default as dac4D } from './dac4D.svelte'
import { default as dac16D } from './dac16D.svelte'
import type { SvelteComponent } from 'svelte'

interface Components {
  dac4D: typeof dac4D;
  dac16D: typeof dac16D;
}

const components: Components = {
    dac4D, 
    dac16D
}

function getComponent(name: keyof Components): typeof dac4D | typeof dac16D {
  return components[name]
}



// I need to make the TotalState.data as an object and find a way to connect the data of that object to the component. 