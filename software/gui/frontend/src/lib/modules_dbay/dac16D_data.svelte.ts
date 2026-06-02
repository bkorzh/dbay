import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";

import { VsourceAddon } from "../addons";
import type { ChSourceState, VsourceChange } from "../addons";
import { ChSourceStateClass, ChSenseStateClass } from "../addons";
import { SvelteSyncNode, type SyncRuntime } from "lab-link/svelte";
import { joinJsonPointer } from "lab-link/core";
import { syncRuntime } from "../../sync/runtime.svelte";

// this class is used to manage the state of the 4 channel differential voltage source.
// It is separate from the UI that describes how the component looks (dac4D.svelte).
// Arguably, you only need a data-holding object defined by an interface instead of a full-fledged class.
// That would be fine, but I like giving unique modules the option of exposing unique methods for operating on the module state.

// such methods could instead be implemented on the backend and exposed with extra API endpoints for each module type.

// 4 channel differential voltage source
export class dac16D extends SvelteSyncNode<JsonModule> implements IModule {
  public vsource: VsourceAddon;
  public core: CoreModule;
  public shared_voltage: ChSourceStateClass;

  public vsb: ChSourceStateClass;
  public vr: ChSenseStateClass;
  private replaceSelf?: (data: JsonModule) => void;

  public link_enabled = $state(Array.from({ length: 16 }, (_, i) => true));

  public fields: any = this.defineFields<any>({
    core: {
      onApplied: () => this.replaceIfTypeChanged(),
    },
    vsource: {
      onApplied: () => this.replaceIfTypeChanged(),
    },
    vsb: {},
    vr: {},
  });


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

  constructor(data: JsonModule);
  constructor(
    sync: SyncRuntime,
    path: string,
    data: JsonModule,
    replaceSelf?: (data: JsonModule) => void,
  );
  constructor(
    syncOrData: SyncRuntime | JsonModule,
    path?: string,
    data?: JsonModule,
    replaceSelf?: (data: JsonModule) => void,
  ) {
    const parsed = data ?? (syncOrData as JsonModule);
    const sync = data ? (syncOrData as SyncRuntime) : syncRuntime;
    const nodePath = path ?? joinJsonPointer("", "data", String(parsed.core.slot));

    super(sync, nodePath);
    this.replaceSelf = replaceSelf;
    this.core = new CoreModule(parsed.core);
    this.vsource = new VsourceAddon(
      sync,
      joinJsonPointer(nodePath, "vsource"),
      parsed.core.slot,
      parsed.vsource?.channels,
      16,
    );

    // used to setting all channels to the same voltage.

    // if channels are set individually, this voltage value becomes irrelevant.
    // the module slot is injected into each ChSourceState, which makes it easier for these low level objects to create valid messages for the backend.
    this.shared_voltage = new ChSourceStateClass(
      sync,
      joinJsonPointer(nodePath, "vsource", "shared_voltage"),
      {
        index: 0,
        bias_voltage: 0,
        activated: false,
        heading_text: "Set Linked Channels",
        measuring: false,
      },
      parsed.core.slot,
    );

    this.vsb = new ChSourceStateClass(
      sync,
      joinJsonPointer(nodePath, "vsb"),
      {
        index: 0,
        bias_voltage: 0,
        activated: false,
        heading_text: "",
        measuring: false,
      },
      parsed.core.slot,
    );

    this.vr = new ChSenseStateClass(
      sync,
      joinJsonPointer(nodePath, "vr"),
      {
        index: 0,
        voltage: 0,
        measuring: false,
        name: "",
      },
      parsed.core.slot,
    );
  }

  public applySnapshot(data: JsonModule): void {
    if (data.core.type !== this.core.type) {
      this.replaceSelf?.(data);
      return;
    }
    this.update(data);
  }

  public update(data: JsonModule): void {
    this.core.update(data.core);
    if (data.vsource)
      this.vsource.update(data.core.slot, data.vsource.channels);
  }

  private replaceIfTypeChanged(): void {
    const latest = this.sync.get<JsonModule>(this.path);
    if (latest.core.type !== "dac16D") this.replaceSelf?.(latest);
  }

  public dispose(): void {
    this.vsource.dispose();
    this.shared_voltage.dispose();
    this.vsb.dispose();
    this.vr.dispose();
    super.dispose();
  }
}
