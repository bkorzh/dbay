Components that correspond to a real-life module for the D-Bay rack go here. These include: 



dac4d: 4-channel differential voltage source module
dac16D: Differential 16-channel voltage source module
...and others...


The top level user interface for a module is defined in files: `{module_name}.svelte`
Core logic for a module is contained in a files: `{module_name}_data.svelte.ts`

The core logic files make use of `addons` that define common interfaces/functionalities shared by multiple modules. 
These include the `vsense` module for ADCs and `vsource` for DACs. 


Logic for instantiating and operating on multiple modules together is contained in `index.svelte.ts`