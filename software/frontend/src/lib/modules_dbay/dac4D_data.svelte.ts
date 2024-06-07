import { VsourceAddon } from "../addons/vsource/vsource.svelte"
import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";
import type { ChSourceState } from "../addons";

// 4 channel differential voltage source
export class dac4D implements IModule {
  public vsource: VsourceAddon;
  public core: CoreModule;

  constructor(data: JsonModule) {
    this.core = new CoreModule(data.core);
    console.log("I'm inside the dac4D constructor and data.vsource.channels is: ", data.vsource?.channels)
    this.vsource = new VsourceAddon(data.core.slot, data.vsource?.channels, 4)
  }

  public update(data: JsonModule): void {
    this.core.update(data.core);
    if (data.vsource) this.vsource.update(data.core.slot, data.vsource.channels);
  }
}
