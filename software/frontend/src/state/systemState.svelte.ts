import { VsourceAddon, VsenseAddon } from "../lib/addons"
import type { IVsourceAddon, IVsenseAddon } from "../lib/addons"
import type { ChSourceState, ChSenseState } from "../lib/addons"


export interface IModule {
  core: CoreModule;
  vsource?: VsourceAddon; // VsourceAddon is a class that implements the IVsourceAddon interface...
  vsense?: VsenseAddon;
}

export interface JsonModule {
  core: JsonCoreModule;
  vsource?: IVsourceAddon;
  vsense?: IVsenseAddon;
}



export interface JsonCoreModule {
  slot: number;
  type: string;
  name: string;
}

export class CoreModule implements JsonCoreModule {
  slot: number;
  type: string;
  name: string = $state("");

  constructor(data: JsonCoreModule) {
      this.slot = data.slot;
      this.type = data.type;
      this.name = data.name;
  }
}


export interface SystemState {
  data: Array<IModule>;
  valid: boolean;
  dev_mode: boolean;
}

export class SystemStateClass implements SystemState {
  data: Array<IModule> = $state([]);
  valid: boolean = $state(false);
  dev_mode: boolean = $state(false);

  constructor(data: Array<IModule>, valid: boolean, dev_mode: boolean) {
    this.data = data;
    this.valid = valid;
    this.dev_mode = dev_mode;
  }
}

export interface JsonSystemState {
  data: Array<JsonModule>;
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

// export const 

export let system_state: SystemState = new SystemStateClass([], false, false);



