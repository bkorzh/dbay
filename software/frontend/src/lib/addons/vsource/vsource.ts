
import type { IVsourceAddon, ChSourceState } from './interface';

export class VsourceAddon implements IVsourceAddon{
    constructor(
      public channels: Array<ChSourceState>) { }
  
      public switchOnOffAllChannels(onoff: boolean): void {
        this.channels.forEach(channel => channel.activated = onoff);
      }
  }