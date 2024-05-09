import type { IVsenseAddon, ChSenseState } from './interface';

export class VsenseAddon implements IVsenseAddon{
    constructor(
      public channels: Array<ChSenseState>) { }
  }