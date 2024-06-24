import type { IVsenseAddon, ChSenseState } from "./interface";

export class ChSenseStateClass implements ChSenseState {
  // interface defined properties
  public index: number;
  public voltage: number = $state(0);
  public measuring: boolean = $state(false);
  public name: string = $state("");

  // module index
  public module_index: number;

  constructor(data: ChSenseState, module_index: number) {
    this.index = data.index;
    this.voltage = data.voltage;
    this.measuring = data.measuring;
    this.name = data.name;

    this.module_index = module_index;
  }
}

export class VsenseAddon implements IVsenseAddon {
  public channels: ChSenseState[];
  constructor(
    module_index: number,
    channels?: Array<ChSenseStateClass>,
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
}
