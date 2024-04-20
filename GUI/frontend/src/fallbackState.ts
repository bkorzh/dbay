import type { Module4chState, SystemState, ChState } from "./stores/voltageStore";

const module_1: Module4chState = {
  channels: [
    { index: 1, bias_voltage: 0.0, activated: false, heading_text: "test 1" },
    { index: 2, bias_voltage: 0.0, activated: false, heading_text: "test 2" },
    { index: 3, bias_voltage: 0.0, activated: false, heading_text: "test 3" },
    { index: 4, bias_voltage: 0.0, activated: false, heading_text: "test 4" },
  ],
  slot: 1,
  type: "4Ch",
  name: "module 1 slot 1"
};

const module_2: Module4chState = {
  channels: [
    { index: 1, bias_voltage: 0.0, activated: false, heading_text: "test 5" },
    { index: 2, bias_voltage: 0.0, activated: false, heading_text: "test 6" },
    { index: 3, bias_voltage: 0.0, activated: false, heading_text: "test 7" },
    { index: 4, bias_voltage: 0.0, activated: false, heading_text: "test 8" },
  ],
  slot: 4,
  type: "4Ch",
  name: "module 2 slot 4"
};

export let fallbackState: SystemState = {data: [module_1, module_2], valid: false};