import type { IVsourceAddon, ChSourceState } from './interface';

export class ChSourceStateClass implements ChSourceState {
  index: number;
  bias_voltage: number = $state(0);
  activated: boolean = $state(false);
  heading_text: string = $state("");
  measuring: boolean = $state(false);

  constructor(data: ChSourceState) {
    this.index = data.index;
    this.bias_voltage = data.bias_voltage;
    this.activated = data.activated;
    this.heading_text = data.heading_text;
    this.measuring = data.measuring;
  }
}



export class VsourceAddon implements IVsourceAddon{
  public channels: ChSourceState[];
    constructor(
      channels?: Array<ChSourceState>, default_channel_number=4) {
        const deflt = !channels || channels.length === 0;
        this.channels = Array.from({length: deflt ? default_channel_number : channels.length}, (_, i) => {

          if (deflt) {
            return new ChSourceStateClass({
              index: i + 1,
              bias_voltage: 0,
              activated: false,
              heading_text: "channel " + (i + 1),
              measuring: false
            });
          } else {
            return new ChSourceStateClass(channels[i]);
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