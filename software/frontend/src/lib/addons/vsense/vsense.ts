// STATE

export interface ChSenseState {
    index: number;
    voltage: number;
    measuring: number;
  }



// OBJECT

export class VsenseAddon {
    constructor(
      public channels: Array<ChSenseState>) { }
  }