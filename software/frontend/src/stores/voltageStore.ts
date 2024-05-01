import { writable } from 'svelte/store';
// import type Module from '../lib/Module.svelte';

export interface ChannelChange {
  module_index: number;
  index: number;
  bias_voltage: number;
  activated: boolean;
  heading_text: string;
  measuring: boolean;
}

export interface ChState {
  index: number;
  bias_voltage: number;
  activated: boolean;
  heading_text: string;
  measuring: boolean;
}

// export interface Module {
//   slot: number;
//   type: string;
//   name: string;
// }

// export interface VoltageSourceModule extends Module {
//   // added to differential bewteen modules that can be 'turned on' and 'turned off'

// }

// export interface Module4chState extends VoltageSourceModule {
//   channels: Array<ChState>,
// }

// // other module types can extend from Module. Like this would be for the peacoq 16ch module
// export interface Module16chState extends VoltageSourceModule {
//   channels: Array<ChState>,
// }

export class Module {
  constructor(
    public slot: number,
    public type: string,
    public name: string) { }
}

export class VoltageSourceModule extends Module {
  constructor(
    slot: number,
    type: string,
    name: string,
    public channels: Array<ChState>) {
    super(slot, type, name);
  }
}

export class Module4chState extends VoltageSourceModule { }

export class Module16chState extends VoltageSourceModule { }



export interface SystemState {
  data: Array<Module>;
  valid: boolean;
}

export interface VsourceParams {
  ipaddr: string;
  timeout: number;
  port: number;
}

function switch_on_off_channel(channel: ChState, onoff: boolean): ChState {
  channel.activated = onoff
  return channel;
}

function switch_on_off_module(module: VoltageSourceModule, onoff: boolean): VoltageSourceModule {
  module.channels.map((channel) => switch_on_off_channel(channel, onoff));
  return module;
}

export function switch_on_off_system(system: SystemState, onoff: boolean): SystemState {
  return {
    data: system.data.map((module) => {
      
      // if it's a type of module that can be turned on and off
      if (module instanceof VoltageSourceModule) {
        return switch_on_off_module(module, onoff);
      }
      return module;
    }),
    valid: system.valid
  };
}



export const voltageStore = writable<SystemState>({ data: [], valid: false });


