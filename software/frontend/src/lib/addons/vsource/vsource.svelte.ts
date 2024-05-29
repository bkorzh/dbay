import type { IVsourceAddon, ChSourceState, VsourceChange } from './interface';


export class ChSourceStateClass implements ChSourceState {
  public index: number;
  public bias_voltage: number = $state(0);
  public activated: boolean = $state(false);
  public heading_text: string = $state("");
  public measuring: boolean = $state(false);



  public temp: Array<number> = $state([0, 0, 0, 0]);
  public sign_temp = $state("+");

  public valid = $state(true);

  integer = $derived(Math.round(Math.abs(this.bias_voltage * 1000)));
  thousands = $derived(this.integer % 10);
  hundreds = $derived(Math.floor(this.integer / 10) % 10);
  tens = $derived(Math.floor(this.integer / 100) % 10);
  ones = $derived(Math.floor(this.integer / 1000) % 10)
  sign = $derived(this.bias_voltage < 0 ? "-" : "+");

  public visible = $state(true);
  public editing = $state(false);
  public isHovering = $state(false);
  public isPlusMinusPressed = $state(false);
  public focusing = $state(false);
  

  constructor(data: ChSourceState) {
    this.index = data.index;
    this.bias_voltage = data.bias_voltage;
    this.activated = data.activated;
    this.heading_text = data.heading_text;
    this.measuring = data.measuring;
  }

  public setChannel(data: VsourceChange) {
    this.bias_voltage = data.bias_voltage;
    this.activated = data.activated;
    this.heading_text = data.heading_text;
    this.measuring = data.measuring;
    this.valid = true;

    // updating bias voltage should update temp and sign_temp, but temp and sign_temp
    // are allowed to get out of sync with bias_voltage (during edit mode of <Channel>)
    this.temp[3] = this.thousands;
    this.temp[2] = this.hundreds;
    this.temp[1] = this.tens;
    this.temp[0] = this.ones;
    this.sign_temp = this.sign;
  }

  public setInvalid(): void {
    this.valid = false;
    
    this.temp[3] = 0;
    this.temp[2] = 0;
    this.temp[1] = 0;
    this.temp[0] = 0;
    this.sign_temp = "+";
    this.activated = false;
  }

  public setValid(data: VsourceChange): void {
    this.valid = true;
    this.setChannel(data);
  }
}



export class VsourceAddon implements IVsourceAddon{
  public channels: ChSourceStateClass[];
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