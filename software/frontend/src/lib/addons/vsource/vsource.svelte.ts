import type { IVsourceAddon, ChSourceState, VsourceChange } from './interface';


export type ChangerFunction = (data: VsourceChange) => Promise<VsourceChange>;

export class ChSourceStateClass implements ChSourceState {

  // interface defined properties
  public index: number;
  public bias_voltage: number = $state(0);
  public activated: boolean = $state(false);
  public heading_text: string = $state("");
  public measuring: boolean = $state(false);

  // module index
  public module_index: number;

  // derived and computed properties
  public temp: Array<number> = $state([0, 0, 0, 0]);
  public sign_temp = $state("+");
  public valid = $state(true);
  public integer = $derived(Math.round(Math.abs(this.bias_voltage * 1000)));
  public thousands = $derived(this.integer % 10);
  public hundreds = $derived(Math.floor(this.integer / 10) % 10);
  public tens = $derived(Math.floor(this.integer / 100) % 10);
  public ones = $derived(Math.floor(this.integer / 1000) % 10)
  public sign = $derived(this.bias_voltage < 0 ? "-" : "+");
  public editing = $state(false);
  public isHovering = $state(false);
  public isPlusMinusPressed = $state(false);
  public focusing = $state(false);

  public heading_editing = $state(false);
  public immediate_text = $state("");


  constructor(data: ChSourceState, module_index: number) {
    this.index = data.index;
    this.bias_voltage = data.bias_voltage;
    this.activated = data.activated;
    this.heading_text = data.heading_text;
    this.measuring = data.measuring;
    this.module_index = module_index;
    this.voltageToTemp();
  }

  public update(data: ChSourceState, module_index: number) {
    this.index = data.index;
    this.bias_voltage = data.bias_voltage;
    this.activated = data.activated;
    this.heading_text = data.heading_text;
    this.measuring = data.measuring;
    this.module_index = module_index;
    this.voltageToTemp();
  }

  public currentStateAsChange(): VsourceChange {
    return {
      index: this.index,
      module_index: this.module_index,
      bias_voltage: this.bias_voltage,
      activated: this.activated,
      heading_text: this.heading_text,
      measuring: this.measuring,
    };
  }


  public async validateUpdateVoltage(voltage: number, onChannelChange: ChangerFunction) {
    if (voltage >= 5) {
      voltage = 5;
    }
    if (voltage <= -5) {
      voltage = -5;
    }
    this.updateChannel({ voltage: voltage }, onChannelChange);
  }

  public onSubmit(onChannelChange: ChangerFunction) {
    const submitted_voltage = parseFloat(
      `${this.sign_temp}${this.temp[0]}.${this.temp[1]}${this.temp[2]}${this.temp[3]}`,
    );

    this.validateUpdateVoltage(submitted_voltage, onChannelChange);

    this.editing = false;
    this.focusing = false;
    this.isPlusMinusPressed = true;
    setTimeout(() => {
      this.isPlusMinusPressed = false;
    }, 1);
  }

  public async updateChannel({
    voltage = this.bias_voltage,
    activated = this.activated,
    heading_text = this.heading_text,
    index = this.index,
    measuring = this.measuring,
  } = {}, onChannelChange: ChangerFunction) {


    const data: VsourceChange = {
      module_index: this.module_index,
      bias_voltage: voltage,
      activated,
      heading_text,
      index,
      measuring,
    };
    const returnData = await onChannelChange(data);
    this.setChannel(returnData);
  }

  public setChannel(data: VsourceChange) {
    this.bias_voltage = data.bias_voltage;
    this.activated = data.activated;
    this.heading_text = data.heading_text;
    this.measuring = data.measuring;
    this.valid = true;

    // updating bias voltage should update temp and sign_temp, but temp and sign_temp
    // are allowed to get out of sync with bias_voltage (during edit mode of <Channel>)
    this.voltageToTemp();
  }

  public voltageToTemp(): void {
    this.temp[3] = this.thousands;
    this.temp[2] = this.hundreds;
    this.temp[1] = this.tens;
    this.temp[0] = this.ones;
    this.sign_temp = this.sign;
    
    if (!this.heading_editing) this.immediate_text = this.heading_text;
  }

  public setInvalid(): void {
    this.valid = false;

    // this.temp[3] = 0;
    // this.temp[2] = 0;
    // this.temp[1] = 0;
    // this.temp[0] = 0;
    // this.sign_temp = "+";
    // this.activated = false;
  }

  public setValid(data: VsourceChange): void {
    this.valid = true;
    this.setChannel(data);
  }
}



export class VsourceAddon implements IVsourceAddon {
  public channels: ChSourceStateClass[];


  constructor(module_index: number, channels?: Array<ChSourceState>, default_channel_number = 4) {

    const deflt = !channels || channels.length === 0;
    this.channels = Array.from({ length: deflt ? default_channel_number : channels.length }, (_, i) => {

      if (deflt) {
        return new ChSourceStateClass({
          index: i,
          bias_voltage: 0,
          activated: false,
          heading_text: "channel " + (i + 1),
          measuring: false
        }, module_index);
      } else {
        return new ChSourceStateClass(channels[i], module_index);
      }
    });
  }

  public update(module_index: number, channels: Array<ChSourceState>): void {
    for (let i = 0; i < this.channels.length; i++) {
      this.channels[i].update(channels[i], module_index);
    }
  }

  public switchOnOffAllChannels(onoff: boolean): void {
    this.channels.forEach(channel => channel.activated = onoff);
  }

  public setAllChannelsVoltage(voltage: number): void {
    this.channels.forEach(channel => channel.bias_voltage = voltage);
  }
}