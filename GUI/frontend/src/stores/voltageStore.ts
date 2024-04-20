import { writable } from 'svelte/store';
import type Module from '../lib/Module.svelte';

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

export interface Module4chState {
  channels: Array<ChState>,
  slot: number;
  type: string;
  name: string;
}

export interface SystemState {
  data: Array<Module4chState>;
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

function switch_on_off_module(module: Module4chState, onoff: boolean): Module4chState {
  module.channels.map((channel) => switch_on_off_channel(channel, onoff));
  return module;
}

export function switch_on_off_system(system: SystemState, onoff: boolean): SystemState {
  return { data: system.data.map((module) => switch_on_off_module(module, onoff)), valid: system.valid };
}



export const voltageStore = writable<SystemState>({ data: [], valid: false });


