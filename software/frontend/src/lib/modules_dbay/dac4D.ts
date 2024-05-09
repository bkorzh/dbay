import { VsourceAddon } from "../addons/vsource/vsource"
import type { IModule } from "../../state/systemState";
import { Module } from "../../state/systemState";
import type { ChSourceState } from "../addons";

// 4 channel differential voltage source
export class dac4D implements IModule {
    public vsource?: VsourceAddon;
    public module: Module;
  
    constructor(module: Module, vsource?: VsourceAddon) {
      this.module = module;

      // If no VsourceAddon is provided, create a default one
      if (!vsource) {
        const chSourceStates: ChSourceState[] = Array.from({length: 4}, (_, i) => ({
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