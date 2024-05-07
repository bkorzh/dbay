import type { Module4chState, SystemState, ChState } from "./state/systemState";

const module_1: Module4chState = {
  channels: [
    { index: 1, bias_voltage: 0.0, activated: false, heading_text: "test 1", measuring: false},
    { index: 2, bias_voltage: 0.0, activated: false, heading_text: "test 2", measuring: false},
    { index: 3, bias_voltage: 0.0, activated: false, heading_text: "test 3", measuring: false},
    { index: 4, bias_voltage: 0.0, activated: false, heading_text: "test 4", measuring: false},
  ],
  slot: 1,
  type: "4Ch",
  name: "module 1 slot 1"
};

const module_2: Module4chState = {
  channels: [
    { index: 1, bias_voltage: 0.0, activated: false, heading_text: "test 5", measuring: false},
    { index: 2, bias_voltage: 0.0, activated: false, heading_text: "test 6", measuring: false},
    { index: 3, bias_voltage: 0.0, activated: false, heading_text: "test 7", measuring: false},
    { index: 4, bias_voltage: 0.0, activated: false, heading_text: "test 8", measuring: false},
  ],
  slot: 4,
  type: "4Ch",
  name: "module 2 slot 4"
};

export let fallbackState: SystemState = {data: [module_1, module_2], valid: false, dev_mode: true};