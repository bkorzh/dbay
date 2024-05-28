/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface ChSenseState {
  index: number;
  voltage: number;
  measuring: boolean;
  name: string;
}
export interface IVsenseAddon {
  channels: ChSenseState[];
}
export interface VsenseChange {
  module_index: number;
  index: number;
  voltage: number;
  measuring: boolean;
  name: string;
}
