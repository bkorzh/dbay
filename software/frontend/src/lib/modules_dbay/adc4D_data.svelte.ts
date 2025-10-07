import { VsenseAddon } from "../addons/vsense/vsense.svelte"
import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";

// 5 channel differential ADC (voltage sense)
export class adc4D implements IModule {
    public vsense: VsenseAddon;
    public core: CoreModule;

    constructor(data: JsonModule) {
        this.core = new CoreModule(data.core);
        // console.log("I'm inside the adc4D constructor and data.vsense.channels is: ", data.vsense?.channels)
        this.vsense = new VsenseAddon(data.core.slot, data.vsense?.channels, 5)
    }

    public update(data: JsonModule): void {
        this.core.update(data.core);
        if (data.vsense) this.vsense.update(data.core.slot, data.vsense.channels);
    }
}
