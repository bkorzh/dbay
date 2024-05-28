import type { IVsenseAddon, ChSenseState } from './interface';

export class VsenseAddon implements IVsenseAddon {
  public channels: ChSenseState[];
  constructor(
    channels?: Array<ChSenseState>, default_channel_number = 4) {
    const deflt = !channels || channels.length === 0;
    this.channels = Array.from({ length: deflt ? default_channel_number : channels.length }, (_, i) => {
      return {}
      // return deflt ? {
      //   // default state
      //   index: i + 1,
      //   voltage: $state(0),
      //   measuring: $state(false),
      //   name: $state("channel " + (i + 1)),
      // } : {
      //   // state from JSON
      //   index: channels[i].index,
      //   voltage: $state(channels[i].voltage),
      //   measuring: $state(channels[i].measuring),
      //   name: $state(channels[i].name),
        
      // }
    });
  }
}
