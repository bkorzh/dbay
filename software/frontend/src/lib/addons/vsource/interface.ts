/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface ChSourceState {
  index: number;
  bias_voltage: number;
  activated: boolean;
  heading_text: string;
  measuring: boolean;
}
export interface IVsourceAddon {
  channels: ChSourceState[];
}
export interface VsourceChange {
  module_index: number;
  index: number;
  bias_voltage: number;
  activated: boolean;
  heading_text: string;
  measuring: boolean;
}
