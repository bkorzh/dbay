import { writable } from 'svelte/store';


import { VsourceAddon, VsenseAddon } from "../lib/addons"
import type { IVsourceAddon, IVsenseAddon } from "../lib/addons"
import type { ChSourceState, ChSenseState } from "../lib/addons"


export interface IModule {
  module: Module;
  vsource?: VsourceAddon; // VsourceAddon is a class that implements the IVsourceAddon interface...
  vsense?: VsenseAddon;
}


// 'core' properties that every module needs
export class Module {
  constructor(
    public slot: number,
    public type: string,
    public name: string) { }
}


export interface SystemState {
  data: Array<IModule>;
  valid: boolean;
  dev_mode: boolean;
}

export interface VMEParams {
  ipaddr: string;
  timeout: number;
  port: number;
  dev_mode: boolean;
}

function switch_on_off_channel(channel: ChSourceState, onoff: boolean): ChSourceState {
  channel.activated = onoff
  return channel;
}



export function switch_on_off_system(system: SystemState, onoff: boolean): SystemState {
  return {
    data: system.data.map((module: IModule) => {
      
      // if it's a type of module that has a VsourceAddon
      if (module.vsource) {
        module.vsource.switchOnOffAllChannels(onoff);
      }
      return module;
    }),
    valid: system.valid,
    dev_mode: system.dev_mode
  };
}

// function switch_on_off_module(module: VoltageSourceModule, onoff: boolean): VoltageSourceModule {
//   module.channels.map((channel) => switch_on_off_channel(channel, onoff));
//   return module;
// }



export const voltageStore = writable<SystemState>({ data: [], valid: false, dev_mode: false});


