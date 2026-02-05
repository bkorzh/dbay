import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";

import { VsourceAddon } from "../addons";
import type { ChSourceState, VsourceChange } from "../addons";
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

  public link_enabled = $state(Array.from({ length: 16 }, (_, i) => true));


  // written as an arrow function to bind the 'this' context to the class instance.
  validateLinks = (): void => {
    let first_true_index = this.link_enabled.findIndex((val) => val === true);
    if (first_true_index === -1) {
      console.log("No linked channels. Loading dummy state");
      const dummy_state: VsourceChange = {
        module_index: this.core.slot,
        index: 0,
        bias_voltage: 0,
        activated: true,
        heading_text: "fake",
        measuring: false,
      };
      this.shared_voltage.setValid(dummy_state, true);
      return;
    }

    // now assuming there's at least one linked channel

    const compare_channel = this.vsource.channels[first_true_index];

    for (let i = 0; i < this.vsource.channels.length; i++) {
      // if the new channel that is edited or newly included does not
      // match every other linked channel, then set the shared_voltage to invalid
      if (this.link_enabled[i] && i !== first_true_index) {
        // console.log("checking channel: ", i, "with ", current_index);
        if (
          this.vsource.channels[i].bias_voltage !==
            compare_channel.bias_voltage ||
          this.vsource.channels[i].activated !== compare_channel.activated
        ) {
          this.shared_voltage.setInvalid();
          return;
        }
      }
    }

    // if we get here, then all linked channels are valid.
    this.shared_voltage.setValid(compare_channel, true);

  }

  constructor(data: JsonModule) {
    this.core = new CoreModule(data.core);
    this.vsource = new VsourceAddon(data.core.slot, data.vsource?.channels, 16);

    // used to setting all channels to the same voltage.

    // if channels are set individually, this voltage value becomes irrelevant.
    // the module slot is injected into each ChSourceState, which makes it easier for these low level objects to create valid messages for the backend.
    this.shared_voltage = new ChSourceStateClass(
      {
        index: 0,
        bias_voltage: 0,
        activated: false,
        heading_text: "Set Linked Channels",
        measuring: false,
      },
      data.core.slot,
    );

    this.vsb = new ChSourceStateClass(
      {
        index: 0,
        bias_voltage: 0,
        activated: false,
        heading_text: "",
        measuring: false,
      },
      data.core.slot,
    );

    this.vr = new ChSenseStateClass(
      {
        index: 0,
        voltage: 0,
        measuring: false,
        name: "",
      },
      data.core.slot,
    );
  }

  public update(data: JsonModule): void {
    this.core.update(data.core);
    if (data.vsource)
      this.vsource.update(data.core.slot, data.vsource.channels);
  }
}
