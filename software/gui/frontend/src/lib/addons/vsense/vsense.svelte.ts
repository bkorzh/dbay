import { SvelteSyncNode, type SyncRuntime } from "lab-link/svelte";
import { joinJsonPointer } from "lab-link/core";
import { requestSenseUpdate } from "../../../api";
import { system_state } from "../../../state/systemState.svelte";
import type { ChSenseState, IVsenseAddon, VsenseChange } from "./interface";

export type SenseChangerFunction = (data: VsenseChange) => Promise<VsenseChange>;
export type SenseEffectFunction = () => void;

export class ChSenseStateClass
  extends SvelteSyncNode<ChSenseState>
  implements ChSenseState
{
  public index: number = 0;
  public voltage: number = $state(0);
  public measuring: boolean = $state(false);
  public name: string = $state("");

  public module_index: number;

  public isHovering = $state(false);
  public focusing = $state(false);

  public name_editing = $state(false);
  public editing = $state(false);

  public immediate_text = $state("");

  public fields: any = this.defineFields<any>({
    index: { writable: false },
    voltage: {
      blockWhen: () => this.editing,
      onBlocked: "queueLatest",
      validateRemote: (value) => typeof value === "number",
      onApplied: () => this.effect(),
    },
    measuring: {
      onApplied: () => this.effect(),
    },
    name: {
      blockWhen: () => this.name_editing,
      onBlocked: "queueLatest",
      onApplied: () => {
        if (!this.name_editing) this.immediate_text = this.name;
        this.effect();
      },
    },
  });

  constructor(
    sync: SyncRuntime,
    path: string,
    data: ChSenseState,
    module_index: number,
  ) {
    super(sync, path);
    this.module_index = module_index;
    this.applySnapshot(data);
  }

  public applySnapshot(data: ChSenseState): void {
    this.update(data, this.module_index);
  }

  public async onChannelChange(data: VsenseChange) {
    let returnData;
    if (system_state.valid) {
      returnData = await requestSenseUpdate(data, "/adc4D/vsense/");
    } else {
      returnData = data;
    }
    return returnData;
  }

  public effect(): void {}

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

  public finishNameEditing(): void {
    this.name_editing = false;
    this.sync.flushQueued(this, "name");
  }
}

export class VsenseAddon
  extends SvelteSyncNode<IVsenseAddon>
  implements IVsenseAddon
{
  public channels: ChSenseStateClass[];

  constructor(
    sync: SyncRuntime,
    path: string,
    module_index: number,
    channels?: Array<ChSenseState>,
    default_channel_number = 4,
  ) {
    super(sync, path);
    const deflt = !channels || channels.length === 0;
    this.channels = Array.from(
      { length: deflt ? default_channel_number : channels.length },
      (_, i) => {
        const data = deflt
          ? {
              index: i,
              voltage: 0,
              measuring: false,
              name: "",
            }
          : channels[i];

        return new ChSenseStateClass(
          sync,
          joinJsonPointer(path, "channels", String(i)),
          data,
          module_index,
        );
      },
    );
  }

  public applySnapshot(data: IVsenseAddon): void {
    this.update(this.channels[0]?.module_index ?? 0, data.channels);
  }

  public update(module_index: number, channels: Array<ChSenseState>): void {
    for (let i = 0; i < channels.length; i++) {
      if (this.channels[i]) {
        this.channels[i].update(channels[i], module_index);
      } else {
        this.channels.push(
          new ChSenseStateClass(
            this.sync,
            joinJsonPointer(this.path, "channels", String(i)),
            channels[i],
            module_index,
          ),
        );
      }
    }

    while (this.channels.length > channels.length) {
      this.channels.pop()?.dispose();
    }
  }

  public dispose(): void {
    this.channels.forEach((channel) => channel.dispose());
    super.dispose();
  }
}
