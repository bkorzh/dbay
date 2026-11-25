import { VsenseAddon } from "../addons/vsense/vsense.svelte"
import type { IModule, JsonModule, AdcPollingState } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";
import { SvelteSyncNode, type SyncRuntime } from "lab-link/svelte";
import { joinJsonPointer } from "lab-link/core";
import { syncRuntime } from "../../sync/runtime.svelte";

// 4 channel differential ADC (voltage sense)
export class adc4D extends SvelteSyncNode<JsonModule> implements IModule {
    public vsense: VsenseAddon;
    public core: CoreModule;
    public polling: AdcPollingState = $state({ running: false, frequency: 2 });
    private replaceSelf?: (data: JsonModule) => void;

    public fields: any = this.defineFields<any>({
        core: {
            onApplied: () => this.replaceIfTypeChanged(),
        },
        vsense: {
            onApplied: () => this.replaceIfTypeChanged(),
        },
        polling: {},
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
        if (parsed.polling) {
            this.polling.running = parsed.polling.running;
            this.polling.frequency = parsed.polling.frequency;
        }
        this.vsense = new VsenseAddon(
            sync,
            joinJsonPointer(nodePath, "vsense"),
            parsed.core.slot,
            parsed.vsense?.channels,
            4,
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
        if (data.polling) {
            this.polling.running = data.polling.running;
            this.polling.frequency = data.polling.frequency;
        }
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
