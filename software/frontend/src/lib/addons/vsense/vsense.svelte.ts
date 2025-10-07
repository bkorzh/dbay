import type { IVsenseAddon, ChSenseState, VsenseChange } from "./interface";
import { system_state } from "../../../state/systemState.svelte";
import { requestChannelUpdate } from "../../../api";

export type SenseChangerFunction = (data: VsenseChange) => Promise<VsenseChange>;
export type SenseEffectFunction = () => void;

export class ChSenseStateClass implements ChSenseState {
  // interface defined properties
  public index: number;
  public voltage: number = $state(0);
  public measuring: boolean = $state(false);
  public name: string = $state("");

  // module index
  public module_index: number;

  // UI state properties (similar to ChSourceStateClass)
  public isHovering = $state(false);
  public focusing = $state(false);

  // editing locks. Prevent server updates to fields currently being edited
  public name_editing = $state(false);
  public editing = $state(false);

  // default onChannelChange function. Can be overridden by a module. 
  public async onChannelChange(data: VsenseChange) {
    let returnData;
    if (system_state.valid) {
      // Create a voltage sensing specific API call
      const response = await fetch("/adc4D/vsense/", {
        method: "PUT",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      returnData = await response.json();
    } else {
      returnData = data;
    }
    return returnData;
  }

  // default effect function. Can be overridden by a module
  public effect(): void { }

  public immediate_text = $state("");

  constructor(data: ChSenseState, module_index: number) {
    this.index = data.index;
    this.voltage = data.voltage;
    this.measuring = data.measuring;
    this.name = data.name;
    this.module_index = module_index;
    this.immediate_text = this.name;
  }

  public update(data: ChSenseState, module_index: number) {
    this.index = data.index;
    this.voltage = data.voltage;
    this.measuring = data.measuring;
    this.name = data.name;
    this.module_index = module_index;
    if (!this.name_editing) this.immediate_text = this.name;
    this.effect();
  }

  public currentStateAsChange(): VsenseChange {
    return {
      index: this.index,
      module_index: this.module_index,
      voltage: this.voltage,
      measuring: this.measuring,
      name: this.name,
    };
  }

  public async updateChannel(
    {
      voltage = this.voltage,
      measuring = this.measuring,
      name = this.name,
      index = this.index,
    } = {},
  ) {
    const data: VsenseChange = {
      module_index: this.module_index,
      voltage,
      measuring,
      name,
      index,
    };
    const returnData = await this.onChannelChange(data);
    this.setChannel(returnData);
    this.effect();
  }

  public setChannel(data: VsenseChange) {
    this.voltage = data.voltage;
    this.measuring = data.measuring;
    this.name = data.name;

    if (!this.name_editing) this.immediate_text = this.name;
  }
}

export class VsenseAddon implements IVsenseAddon {
  public channels: ChSenseStateClass[];
  constructor(
    module_index: number,
    channels?: Array<ChSenseState>,
    default_channel_number = 4,
  ) {
    const deflt = !channels || channels.length === 0;
    this.channels = Array.from(
      { length: deflt ? default_channel_number : channels.length },
      (_, i) => {
        if (deflt) {
          return new ChSenseStateClass(
            {
              index: i,
              voltage: 0,
              measuring: false,
              name: "",
            },
            module_index,
          );
        } else {
          return new ChSenseStateClass(channels[i], module_index);
        }
      },
    );
  }

  public update(module_index: number, channels: Array<ChSenseState>): void {
    for (let i = 0; i < this.channels.length; i++) {
      if (i < channels.length) {
        // Use the ChSenseStateClass update method
        this.channels[i].update(channels[i], module_index);
      }
    }
  }
}
