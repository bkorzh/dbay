import { VsenseAddon } from "../addons/vsense/vsense.svelte"
import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";
import { SvelteSyncNode, type SyncRuntime } from "lab-link/svelte";
import { joinJsonPointer } from "lab-link/core";
import { syncRuntime } from "../../sync/runtime.svelte";

// 5 channel differential ADC (voltage sense)
export class adc4D extends SvelteSyncNode<JsonModule> implements IModule {
    public vsense: VsenseAddon;
    public core: CoreModule;
    private replaceSelf?: (data: JsonModule) => void;

    public fields: any = this.defineFields<any>({
        core: {
            onApplied: () => this.replaceIfTypeChanged(),
        },
        vsense: {
            onApplied: () => this.replaceIfTypeChanged(),
        },
    });

    constructor(data: JsonModule);
    constructor(
        sync: SyncRuntime,
        path: string,
        data: JsonModule,
        replaceSelf?: (data: JsonModule) => void,
    );
    constructor(
        syncOrData: SyncRuntime | JsonModule,
        path?: string,
        data?: JsonModule,
        replaceSelf?: (data: JsonModule) => void,
    ) {
        const parsed = data ?? (syncOrData as JsonModule);
        const sync = data ? (syncOrData as SyncRuntime) : syncRuntime;
        const nodePath = path ?? joinJsonPointer("", "data", String(parsed.core.slot));

        super(sync, nodePath);
        this.replaceSelf = replaceSelf;
        this.core = new CoreModule(parsed.core);
        // console.log("I'm inside the adc4D constructor and data.vsense.channels is: ", data.vsense?.channels)
        this.vsense = new VsenseAddon(
            sync,
            joinJsonPointer(nodePath, "vsense"),
            parsed.core.slot,
            parsed.vsense?.channels,
            5,
        )
    }

    public applySnapshot(data: JsonModule): void {
        if (data.core.type !== this.core.type) {
            this.replaceSelf?.(data);
            return;
        }
        this.update(data);
    }

    public update(data: JsonModule): void {
        this.core.update(data.core);
        if (data.vsense) this.vsense.update(data.core.slot, data.vsense.channels);
    }

    private replaceIfTypeChanged(): void {
        const latest = this.sync.get<JsonModule>(this.path);
        if (latest.core.type !== "adc4D") this.replaceSelf?.(latest);
    }

    public dispose(): void {
        this.vsense.dispose();
        super.dispose();
    }
}
