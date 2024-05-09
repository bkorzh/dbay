import type { IModule } from "../../state/systemState"
import { Module } from "../../state/systemState"

import { VsourceAddon } from "../addons/";
import type { ChSourceState } from "../addons";


// this class is used to manage the state of the 4 channel differential voltage source. 
// It is separate from the UI that describes how the component looks (dac4D.svelte). 
// Arguably, you only need a data-holding object defined by an interface instead of a full-fledged class.
// That would be fine, but I like giving unique modules the option of exposing unique methods for operating on the module state.

// such methods could instead be implemented on the backend and exposed with extra API endpoints for each module type.


// 4 channel differential voltage source
export class dac16D implements IModule {
    public vsource?: VsourceAddon;
    public module: Module;
  
    constructor(module: Module, vsource?: VsourceAddon) {
      this.module = module;

      // If no VsourceAddon is provided, create a default one
      if (!vsource) {
        const chSourceStates: ChSourceState[] = Array.from({length: 16}, (_, i) => ({
            index: i + 1, 
            bias_voltage: 0, 
            activated: false, 
            heading_text: "detector index " + (i + 1), 
            measuring: false
          }));

        this.vsource = new VsourceAddon(chSourceStates);
      }
    }
}