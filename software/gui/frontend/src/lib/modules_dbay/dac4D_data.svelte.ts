import { VsourceAddon } from "../addons/vsource/vsource.svelte"
import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";
import { SvelteSyncNode, type SyncRuntime } from "lab-link/svelte";
import { joinJsonPointer } from "lab-link/core";
import { syncRuntime } from "../../sync/runtime.svelte";

// 4 channel differential voltage source
export class dac4D extends SvelteSyncNode<JsonModule> implements IModule {
  public vsource: VsourceAddon;
  public core: CoreModule;
  private replaceSelf?: (data: JsonModule) => void;

  public fields: any = this.defineFields<any>({
    core: {
      onApplied: () => this.replaceIfTypeChanged(),
    },
    vsource: {
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
    // console.log("I'm inside the dac4D constructor and data.vsource.channels is: ", data.vsource?.channels)
    this.vsource = new VsourceAddon(
      sync,
      joinJsonPointer(nodePath, "vsource"),
      parsed.core.slot,
      parsed.vsource?.channels,
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
    if (data.vsource) this.vsource.update(data.core.slot, data.vsource.channels);
  }

  private replaceIfTypeChanged(): void {
    const latest = this.sync.get<JsonModule>(this.path);
    if (latest.core.type !== "dac4D") this.replaceSelf?.(latest);
  }

  public dispose(): void {
    this.vsource.dispose();
    super.dispose();
  }
}
