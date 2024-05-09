// import type { Module4chState, SystemState, ChState } from "./state/systemState";

import { dac4D } from "./lib/modules_dbay/dac4D_data.svelte";
import { dac16D } from "./lib/modules_dbay/dac16D_data.svelte";
import type { CoreModule } from "./state/systemState.svelte";
import { VsourceAddon } from "./lib/addons";
import { VsenseAddon } from "./lib/addons";
import type { ChSourceState } from "./lib/addons";

import type { SystemState } from "./state/systemState.svelte";

// const module_1: Module4chState = {
//   channels: [
//     { index: 1, bias_voltage: 0.0, activated: false, heading_text: "test 1", measuring: false},
//     { index: 2, bias_voltage: 0.0, activated: false, heading_text: "test 2", measuring: false},
//     { index: 3, bias_voltage: 0.0, activated: false, heading_text: "test 3", measuring: false},
//     { index: 4, bias_voltage: 0.0, activated: false, heading_text: "test 4", measuring: false},
//   ],
//   slot: 1,
//   type: "4Ch",
//   name: "module 1 slot 1"
// };

// const module_2: Module4chState = {
//   channels: [
//     { index: 1, bias_voltage: 0.0, activated: false, heading_text: "test 5", measuring: false},
//     { index: 2, bias_voltage: 0.0, activated: false, heading_text: "test 6", measuring: false},
//     { index: 3, bias_voltage: 0.0, activated: false, heading_text: "test 7", measuring: false},
//     { index: 4, bias_voltage: 0.0, activated: false, heading_text: "test 8", measuring: false},
//   ],
//   slot: 4,
//   type: "4Ch",
//   name: "module 2 slot 4"
// };


// these use default VsourceAddon objects internally
const module_1: dac4D = new dac4D({core: {slot: 1, type: "dac4D", name: "my 4ch module 1"}});
const module_2: dac4D = new dac4D({core: {slot: 1, type: "dac4D", name: "my 4ch module 1"}});
const module_3: dac16D = new dac16D({core: {slot: 1, type: "dac4D", name: "my 4ch module 1"}});

export let fallbackState: SystemState = {data: $state([module_1, module_2, module_3]), valid: false, dev_mode: true};