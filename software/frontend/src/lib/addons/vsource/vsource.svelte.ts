import type { IVsourceAddon, ChSourceState } from './interface';

export class VsourceAddon implements IVsourceAddon{
  public channels: ChSourceState[];
    constructor(
      channels?: Array<ChSourceState>, default_channel_number=4) {
        const deflt = !channels || channels.length === 0;
        this.channels = Array.from({length: deflt ? default_channel_number : channels.length}, (_, i) => {
          return deflt ? {
            // default state
            index: i + 1,
            bias_voltage: $state(0),
            activated: $state(false),
            heading_text: $state("channel " + (i + 1)),
            measuring: $state(false)
          } : {
            // state from JSON
            index: channels[i].index,
            bias_voltage: $state(channels[i].bias_voltage),
            activated: $state(channels[i].activated),
            heading_text: $state(channels[i].heading_text),
            measuring: $state(channels[i].measuring)
          }
        });
      }
  
      public switchOnOffAllChannels(onoff: boolean): void {
        this.channels.forEach(channel => channel.activated = onoff);
      }

      public setAllChannelsVoltage(voltage: number): void {
        this.channels.forEach(channel => channel.bias_voltage = voltage);
      }
  }