import type { IModule } from "../../state/systemState"
import { Module } from "../../state/systemState"

import { VsourceAddon } from "../addons/";



// 16 channel differential voltage source
export class dac16D implements IModule {
    public vsource: VsourceAddon;
    public module: Module;
  
    constructor(module: Module) {
      this.module = module;
      this.vsource = new VsourceAddon(Array(16).fill({ voltage: 0, current: 0 }));
    }
  }