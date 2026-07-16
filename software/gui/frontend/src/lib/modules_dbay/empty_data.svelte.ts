import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";
import { SvelteSyncNode, type SyncRuntime } from "lab-link/svelte";
import { joinJsonPointer } from "lab-link/core";
import { syncRuntime } from "../../sync/runtime.svelte";

// module placeholder
export class empty extends SvelteSyncNode<JsonModule> implements IModule {
  public core: CoreModule;
  public vsource?: any;
  public vsense?: any;
  private replaceSelf?: (data: JsonModule) => void;

  public fields: any = this.defineFields<any>({
    core: {
      onApplied: () => this.replaceIfTypeChanged(),
    },
    vsource: {
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
  }

  private replaceIfTypeChanged(): void {
    const latest = this.sync.get<JsonModule>(this.path);
    if (latest.core.type !== "empty") this.replaceSelf?.(latest);
  }
}
