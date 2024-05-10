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
          // let index = deflt ? i + 1 : channels[i].index;
          // let bias_voltage = deflt ? $state(0) : $state(channels[i].bias_voltage);
          // let activated = deflt ? $state(false) : $state(channels[i].activated);
          // let heading_text = deflt ? $state("channel " + (i + 1)) : $state(channels[i].heading_text);
          // let measuring = deflt ? $state(false) : $state(channels[i].measuring);
          // return {
          //   index,
          //   get bias_voltage() { return bias_voltage },
          //   set bias_voltage(v) { bias_voltage = v; },
          //   get activated() { return activated },
          //   set activated(v) { activated = v; },
          //   get heading_text() { return heading_text },
          //   set heading_text(v) { heading_text = v; },
          //   get measuring() { return measuring },
          //   set measuring(v) { measuring = v; },
          // }
        });
      }
  
      public switchOnOffAllChannels(onoff: boolean): void {
        this.channels.forEach(channel => channel.activated = onoff);
      }

      public setAllChannelsVoltage(voltage: number): void {
        this.channels.forEach(channel => channel.bias_voltage = voltage);
      }
  }