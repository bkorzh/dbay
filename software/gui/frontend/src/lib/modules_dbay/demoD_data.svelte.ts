import { VsourceAddon } from "../addons/vsource/vsource.svelte";
import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";
import { SvelteSyncNode, type SyncRuntime } from "lab-link/svelte";
import { joinJsonPointer } from "lab-link/core";
import { syncRuntime } from "../../sync/runtime.svelte";

/**
 * demoD — the worked example from the Adding a Module guide. Not real hardware.
 *
 * A module class is a *mirror*: the backend owns the state, and this object is
 * a local view of one slot that lab-link keeps up to date. It holds no truth of
 * its own. Two kinds of field are on display here:
 *
 *  - `vsource`, a nested addon that brings its own UI components with it
 *  - `trim_voltage`, a plain number mirrored directly at this module's path
 */
export class demoD extends SvelteSyncNode<JsonModule> implements IModule {
  public core: CoreModule;
  public vsource: VsourceAddon;

  // $state makes this reactive: any component reading it re-renders when a
  // patch from the server changes it.
  public trim_voltage: number = $state(0);

  // True while the user is dragging the slider. See `blockWhen` below.
  public dragging = $state(false);

  private replaceSelf?: (data: JsonModule) => void;

  /**
   * Declares how incoming patches are applied to each field. Anything not
   * listed here is ignored by the sync runtime.
   */
  public fields: any = this.defineFields<any>({
    core: {
      onApplied: () => this.replaceIfTypeChanged(),
    },
    vsource: {
      onApplied: () => this.replaceIfTypeChanged(),
    },
    trim_voltage: {
      // While a drag is in progress the server's value would fight the user's
      // thumb, so hold updates and apply only the most recent one on release.
      blockWhen: () => this.dragging,
      onBlocked: "queueLatest",
      validateRemote: (value: unknown) => typeof value === "number",
      coerceRemote: (value: unknown) => Math.round(Number(value) * 1000) / 1000,
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
    // Two ways in: the full form the runtime uses, and a data-only form that
    // tests and the offline fallback state use.
    const parsed = data ?? (syncOrData as JsonModule);
    const sync = data ? (syncOrData as SyncRuntime) : syncRuntime;
    const nodePath = path ?? joinJsonPointer("", "data", String(parsed.core.slot));

    super(sync, nodePath);
    this.replaceSelf = replaceSelf;
    this.core = new CoreModule(parsed.core);
    this.trim_voltage = parsed.trim_voltage ?? 0;

    // Child nodes get their own path, built from this module's: the addon
    // mirrors /data/<slot>/vsource. demoD has a single channel.
    this.vsource = new VsourceAddon(
      sync,
      joinJsonPointer(nodePath, "vsource"),
      parsed.core.slot,
      parsed.vsource?.channels,
      1,
    );
  }

  /** A whole-module replacement arrived (initial snapshot, or a reconnect). */
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
    if (data.trim_voltage !== undefined) this.trim_voltage = data.trim_voltage;
  }

  /** The slot's module type changed under us; hand the slot to the right class. */
  private replaceIfTypeChanged(): void {
    const latest = this.sync.get<JsonModule>(this.path);
    if (latest.core.type !== "demoD") this.replaceSelf?.(latest);
  }

  public dispose(): void {
    this.vsource.dispose();
    super.dispose();
  }
}
