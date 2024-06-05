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
    this.vsource = new VsourceAddon(data.core.slot, data.vsource?.channels, 4)
  }

  public update(data: JsonModule): void {
    this.core.update(data.core);
    this.vsource.update(data.core.slot, data.vsource.channels);
  }
}
