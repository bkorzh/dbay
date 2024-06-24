import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte"

import { VsourceAddon } from "../addons";
import type { ChSourceState } from "../addons";
import { ChSourceStateClass, ChSenseStateClass } from "../addons";


// this class is used to manage the state of the 4 channel differential voltage source. 
// It is separate from the UI that describes how the component looks (dac4D.svelte). 
// Arguably, you only need a data-holding object defined by an interface instead of a full-fledged class.
// That would be fine, but I like giving unique modules the option of exposing unique methods for operating on the module state.

// such methods could instead be implemented on the backend and exposed with extra API endpoints for each module type.


// 4 channel differential voltage source
export class dac16D implements IModule {
  public vsource: VsourceAddon;
  public core: CoreModule;
  public shared_voltage: ChSourceStateClass;

  public vsb: ChSourceStateClass;
  public vr: ChSenseStateClass;

  constructor(data: JsonModule) {
    this.core = new CoreModule(data.core);
    this.vsource = new VsourceAddon(data.core.slot, data.vsource?.channels, 16)

    // used to setting all channels to the same voltage.

    // if channels are set individually, this voltage value becomes irrelevant.
    // the module slot is injected into each ChSourceState, which makes it easier for these low level objects to create valid messages for the backend.
    this.shared_voltage = new ChSourceStateClass({
      index: 0,
      bias_voltage: 0,
      activated: false,
      heading_text: "Set Linked Channels",
      measuring: false
    }, data.core.slot);

    this.vsb = new ChSourceStateClass({
      index: 0,
      bias_voltage: 0,
      activated: false,
      heading_text: "",
      measuring: false
    }, data.core.slot);

    this.vr = new ChSenseStateClass({
      index: 0,
      voltage: 0,
      measuring: false,
      name: ""
    }, data.core.slot);

  }

  public update(data: JsonModule): void {
    this.core.update(data.core);
    if (data.vsource) this.vsource.update(data.core.slot, data.vsource.channels);
    
  }
}