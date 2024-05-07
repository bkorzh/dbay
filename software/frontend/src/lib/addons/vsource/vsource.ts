



export interface ChSourceState {
    index: number;
    bias_voltage: number;
    activated: boolean;
    heading_text: string;
    measuring: boolean;
  }
  

export class VsourceAddon {
    constructor(
      public channels: Array<ChSourceState>) { }
  
      public switchOnOffAllChannels(onoff: boolean): void {
        this.channels.forEach(channel => channel.activated = onoff);
      }
  }