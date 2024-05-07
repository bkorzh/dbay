import { VsourceAddon } from "../addons/vsource/vsource"
import type { IModule } from "../../state/systemState";
import { Module } from "../../state/systemState";


// 4 channel differential voltage source
export class dac4D implements IModule {
    public vsource: VsourceAddon;
    public module: Module;
  
    constructor(module: Module) {
      this.module = module;
      this.vsource = new VsourceAddon(Array(4).fill({ voltage: 0, current: 0 }));
    }
  }