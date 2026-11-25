# dbay + lab-link Integration Handoff

This document is the handoff for using the rewritten `lab-link` library in dbay.
The Python import package is `lab_link`; the PyPI and npm package name is
`lab-link`.

The goal is to replace dbay's current frontend long polling of `/full-state`
with server-authoritative WebSocket synchronization, while preserving dbay's
existing domain patterns:

- FastAPI backend owns authoritative device state.
- Backend commands talk to hardware and can fail.
- Frontend state is not plain JSON; it is hydrated into Svelte-oriented
  TypeScript classes with methods, `$state`, `$derived`, edit buffers, and local
  UI flags.
- Errors from failed hardware commands must be visible in the UI.

The motivating library checkout on this machine is currently:

`/Users/andrew/Documents/PROGRAM_LOCAL/lab_sync`

If the local folder is later renamed to match the package/repo name, use:

`/Users/andrew/Documents/PROGRAM_LOCAL/lab-link`

The dbay repo is:

`/Users/andrew/Documents/PROGRAM_LOCAL/dbay`

## Current dbay State Flow

Current frontend polling lives in:

`software/gui/frontend/src/App.svelte`

The app calls `getFullState()` once, then calls it every second:

```ts
intervalId = setInterval(async () => {
  json_state = await getFullState();
  updateSystemStatefromJson(json_state);
}, 1000);
```

Current backend state endpoint lives in:

`software/gui/backend/backend/main.py`

```python
@app.get("/full-state")
async def state():
    return global_state.system_state
```

Module mutation endpoints currently mutate `global_state.system_state` and talk
to hardware, for example:

- `backend/modules/dac4D.py`
- `backend/modules/dac16D.py`
- `backend/modules/adc4D.py`

The integration should replace polling first. Do not start by rewriting all dbay
module classes or deleting the REST endpoints.

## Recommended Migration Strategy

Use three phases.

### Phase 1: Add lab-link beside existing REST

Add `/sync/ws` and `/sync/state` to the FastAPI backend.

Keep existing REST endpoints working. Whenever an existing REST endpoint mutates
`global_state.system_state`, also update `lab-link` so all WebSocket clients see
the change.

This phase removes long polling without changing every module command at once.

### Phase 2: Convert frontend polling to snapshot/patch

The frontend should connect to `ws://127.0.0.1:8345/sync/ws` in Tauri/dev mode
and use snapshots/patches instead of polling.

Initially, it is acceptable for every patch to update from the runtime's latest
snapshot:

```ts
runtime.onPatch(() => {
  const latest = runtime.snapshot();
  if (latest) updateSystemStatefromJson(latest);
});
```

That is not the final architecture, but it is still a strict improvement over
polling. It validates the backend sync path before rewriting class models.

### Phase 3: Move dbay classes to SyncNode/SvelteSyncNode

After the WebSocket transport is stable, migrate the frontend state classes to
class-backed sync nodes:

- `ChSourceStateClass`
- `ChSenseStateClass`
- `VsourceAddon`
- `VsenseAddon`
- `dac4D`
- `dac16D`
- `adc4D`
- `SystemStateClass` or a new root model

This lets patches route directly to the affected channel/module and allows
field-level policies such as `blockWhen: () => this.editing`.

## Dependency Setup

Use the published PyPI and npm packages. Local path linking is not required for
normal dbay integration.

Backend:

```bash
cd /Users/andrew/Documents/PROGRAM_LOCAL/dbay/software/gui/backend
uv add lab-link
```

Frontend:

```bash
cd /Users/andrew/Documents/PROGRAM_LOCAL/dbay/software/gui/frontend
bun add lab-link
```

After installation, the backend dependency should look like this:

Backend `software/gui/backend/pyproject.toml` should add:

```toml
dependencies = [
    "dbay",
    "fastapi[standard]>=0.115.6",
    "psutil>=6.1.0",
    "pyinstaller>=6.11.1",
    "lab-link",
]

[tool.uv.sources]
dbay = { path = "../../client", editable = true }
```

The frontend dependency should look like this:

```json
{
  "dependencies": {
    "lab-link": "^0.1.1"
  }
}
```

For active `lab-link` development only, a local override can be used. On the
current machine, the checkout is still named `lab_sync`, so the local paths
would be:

```toml
lab-link = { path = "../../../../lab_sync/python", editable = true }
```

```json
{
  "dependencies": {
    "lab-link": "file:../../../../lab_sync/js"
  }
}
```

If the checkout is later renamed to `lab-link`, switch those paths to
`../../../../lab-link/python` and `../../../../lab-link/js`.

## Backend Integration

Create a small sync module, for example:

`software/gui/backend/backend/sync.py`

```python
from lab_link import LabSync

sync = LabSync()
```

Then wire it into `main.py`.

```python
from contextlib import asynccontextmanager
from backend.sync import sync
from backend.state import SystemState
from backend.initialize import global_state

sync.register_state(SystemState, initial=global_state.system_state)

@asynccontextmanager
async def lifespan(app):
    async with sync.lifespan(app):
        yield

app = FastAPI(lifespan=lifespan)
app.include_router(sync.router)
```

Keep the existing routers and static serving. Do not use `sync.create_app()` in
dbay because dbay already has custom routes, static assets, CORS, and shutdown
handling.

## Backend State Authority

During migration, dbay will temporarily have two state representations:

- `global_state.system_state`: existing Pydantic state object used by current
  backend code and controllers.
- `lab-link` `StateStore`: JSON-serializable validated copy used for snapshot
  and patch broadcasts.

Keep them in sync explicitly.

For narrow field updates, mutate `global_state.system_state` and apply matching
`sync.transaction()` updates.

For broad structural updates, such as adding/replacing a module, mutate
`global_state.system_state` and call:

```python
sync.replace_state(global_state.system_state)
```

Long term, dbay may make `lab-link` the only state commit path, but that is not
required for the first integration.

## JSON Pointer Paths

Use `lab_link.ptr()` on the backend. Do not hand-build JSON Pointer strings.

```python
from lab_link import ptr

channel_path = ptr("data", slot, "vsource", "channels", channel)
voltage_path = ptr("data", slot, "vsource", "channels", channel, "bias_voltage")
```

This matters because JSON Pointer requires escaping `/` and `~` inside path
segments.

Common dbay paths:

```python
ptr("data", slot)
ptr("data", slot, "core", "name")
ptr("data", slot, "vsource", "channels", channel)
ptr("data", slot, "vsource", "channels", channel, "bias_voltage")
ptr("data", slot, "vsource", "channels", channel, "activated")
ptr("data", slot, "vsource", "channels", channel, "heading_text")
ptr("data", slot, "vsense", "channels", channel, "voltage")
ptr("dev_mode")
```

## Backend Command Pattern

Use WebSocket commands for new code. A command should:

1. Validate the requested module/slot/channel.
2. Compute canonical values, such as rounded voltages.
3. Perform the hardware side effect.
4. If hardware fails, raise `CommandError` before committing state.
5. Mutate `global_state.system_state`.
6. Commit matching `lab-link` state changes in one transaction.
7. Return a canonical result payload.

Example for a DAC channel command:

```python
from typing import cast

from lab_link import CommandContext, CommandError, ptr
from backend.sync import sync
from backend.initialize import global_state
from backend.modules.dac4D_spec import dac4D, dac4DController


@sync.command
def set_dac4d_vsource(
    ctx: CommandContext,
    module_index: int,
    index: int,
    bias_voltage: float,
    activated: bool,
    heading_text: str,
    measuring: bool,
):
    try:
        module = cast(dac4D, global_state.system_state.data[module_index])
    except IndexError as exc:
        raise CommandError(
            code="invalid_module_index",
            message=f"Module index {module_index} does not exist.",
            display="toast",
            severity="warning",
            recoverable=True,
        ) from exc

    if module.core.type != "dac4D":
        raise CommandError(
            code="wrong_module_type",
            message=f"Slot {module_index + 1} is not a dac4D module.",
            display="toast",
            severity="warning",
            path=ptr("data", module_index),
            recoverable=True,
        )

    if index < 0 or index > 3:
        raise CommandError(
            code="invalid_channel_index",
            message=f"Channel {index} is outside the dac4D range.",
            display="toast",
            severity="warning",
            path=ptr("data", module_index, "vsource"),
            recoverable=True,
        )

    canonical_voltage = round(bias_voltage, 4)
    if canonical_voltage < -5 or canonical_voltage > 5:
        raise CommandError(
            code="voltage_out_of_range",
            message=f"{canonical_voltage} V is outside the allowed range.",
            display="toast",
            severity="warning",
            path=ptr("data", module_index, "vsource", "channels", index, "bias_voltage"),
            recoverable=True,
        )

    controller = cast(dac4DController, global_state.controllers[module_index])
    hardware_voltage = canonical_voltage if activated else 0

    try:
        result = controller.setChVol(module_index, index, hardware_voltage)
    except Exception as exc:
        raise CommandError(
            code="hardware_command_failed",
            message="The voltage source command failed.",
            detail=repr(exc),
            display="banner",
            severity="error",
            path=ptr("data", module_index, "vsource", "channels", index),
            recoverable=True,
        ) from exc

    if result != 0:
        raise CommandError(
            code="hardware_error_code",
            message="The voltage source returned an error.",
            detail=f"setChVol returned {result}",
            display="banner",
            severity="error",
            path=ptr("data", module_index, "vsource", "channels", index),
            recoverable=True,
        )

    channel = module.vsource.channels[index]
    channel.bias_voltage = canonical_voltage
    channel.activated = activated
    channel.heading_text = heading_text
    channel.measuring = measuring

    channel_path = ptr("data", module_index, "vsource", "channels", index)
    with sync.transaction() as tx:
        tx.set(ptr("data", module_index, "vsource", "channels", index, "bias_voltage"), canonical_voltage)
        tx.set(ptr("data", module_index, "vsource", "channels", index, "activated"), activated)
        tx.set(ptr("data", module_index, "vsource", "channels", index, "heading_text"), heading_text)
        tx.set(ptr("data", module_index, "vsource", "channels", index, "measuring"), measuring)

    return {
        "module_index": module_index,
        "index": index,
        "bias_voltage": canonical_voltage,
        "activated": activated,
        "heading_text": heading_text,
        "measuring": measuring,
        "path": channel_path,
    }
```

Notice that the hardware command happens before the state commit. That avoids
advertising a server state that the hardware did not accept.

## Existing REST Endpoint Bridge

During Phase 1, keep existing REST endpoints but broadcast updates through
`lab-link`.

For example, after `global_state.add_module(...)`:

```python
@app.post("/initialize-module")
async def init_module(request: Request, addition_args: ModuleAddition):
    global_state.add_module(addition_args.type, addition_args.slot)
    sync.replace_state(global_state.system_state)
    return global_state.system_state
```

For `/initialize-vsource`:

```python
@app.post("/initialize-vsource")
async def vsource_set_state(params: VsourceParams):
    global_state.system_state.dev_mode = params.dev_mode
    parent_udp.udp = UDP(params.ipaddr, params.port, params.dev_mode)
    sync.set(ptr("dev_mode"), params.dev_mode)
    return params
```

For module field updates, prefer a transaction over `replace_state()` so clients
receive small patches.

## Frontend Runtime Setup

Create:

`software/gui/frontend/src/sync/runtime.svelte.ts`

```ts
import { createSyncRuntime, type SyncRuntime } from "lab-link/svelte";
import type { JsonSystemState } from "../state/systemState.svelte";

function backendWsUrl() {
  const isTauri = "__TAURI_INTERNALS__" in window;
  const useBackendBaseUrl = isTauri || import.meta.env.DEV;

  if (useBackendBaseUrl) {
    return "ws://127.0.0.1:8345/sync/ws";
  }

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/sync/ws`;
}

export const syncRuntime: SyncRuntime<JsonSystemState> =
  createSyncRuntime<JsonSystemState>({
    url: backendWsUrl(),
    autoConnect: false,
    commandTimeoutMs: 10_000,
  });
```

Connect in `App.svelte`:

```ts
import { onMount, onDestroy } from "svelte";
import { syncRuntime } from "./sync/runtime.svelte";
import {
  createSystemStatefromJson,
  updateSystemStatefromJson,
  updateSystemStatetoFallback,
} from "./lib/modules_dbay/index.svelte";

let didCreateState = false;
let unsubSnapshot: (() => void) | undefined;
let unsubPatch: (() => void) | undefined;
let unsubStatus: (() => void) | undefined;
let unsubErrors: (() => void) | undefined;

onMount(() => {
  unsubSnapshot = syncRuntime.onSnapshot(({ data }) => {
    if (!didCreateState) {
      createSystemStatefromJson(data);
      didCreateState = true;
      return;
    }
    updateSystemStatefromJson(data);
  });

  // Phase 2 simple mode: use runtime snapshot after each patch.
  // Phase 3 class mode should remove this and rely on SyncNode routing.
  unsubPatch = syncRuntime.onPatch(() => {
    const latest = syncRuntime.snapshot();
    if (latest && didCreateState) updateSystemStatefromJson(latest);
  });

  unsubErrors = syncRuntime.onCommandError((error) => {
    syncErrors.add(error);
  });

  syncRuntime.connect();
});

onDestroy(() => {
  unsubSnapshot?.();
  unsubPatch?.();
  unsubStatus?.();
  unsubErrors?.();
  syncRuntime.disconnect();
});
```

The code above is the staged version. It validates the sync transport without
requiring every class to be a `SyncNode` yet.

## Frontend Error Store

Create a small Svelte state store for command errors:

`software/gui/frontend/src/sync/errors.svelte.ts`

```ts
import type { SyncCommandError } from "lab-link/core";

export interface DisplayError {
  id: string;
  message: string;
  detail?: string;
  code: string;
  severity: "info" | "warning" | "error";
  display: "toast" | "banner" | "inline";
  path?: string;
  recoverable: boolean;
  createdAt: number;
}

export const syncErrors = $state({
  banner: null as DisplayError | null,
  toasts: [] as DisplayError[],
  byPath: new Map<string, DisplayError>(),

  add(error: SyncCommandError) {
    const item: DisplayError = {
      id: `${error.code}-${Date.now()}-${Math.random()}`,
      message: error.message,
      detail: error.detail,
      code: error.code,
      severity: error.severity,
      display: error.display,
      path: error.path,
      recoverable: error.recoverable,
      createdAt: Date.now(),
    };

    if (item.display === "banner") {
      this.banner = item;
      return;
    }

    if (item.display === "inline" && item.path) {
      this.byPath.set(item.path, item);
      return;
    }

    this.toasts.push(item);
  },

  clearBanner() {
    this.banner = null;
  },

  clearPath(path: string) {
    this.byPath.delete(path);
  },
});
```

Display `syncErrors.banner` near the top of `App.svelte` or `TopControls`.
Display inline errors in channel components by looking up the channel path.

## Phase 3: Class-Backed SyncNode Pattern

When migrating dbay classes, use `SvelteSyncNode` from `lab-link/svelte`.

The important rule is:

Only server-authoritative fields go in `fields`. Local UI fields do not.

Server fields:

- `bias_voltage`
- `activated`
- `heading_text`
- `measuring`
- ADC `voltage`
- ADC `name`
- module `core` fields

Local UI fields:

- `editing`
- `heading_editing`
- `name_editing`
- `temp`
- `sign_temp`
- `valid`
- `isHovering`
- `focusing`
- dropdown states
- collapsed/expanded UI state

Example channel model:

```ts
import {
  SvelteSyncNode,
  type SyncRuntime,
  joinJsonPointer,
} from "lab-link/svelte";
import type { ChSourceState, VsourceChange } from "./interface";

export class ChSourceStateClass extends SvelteSyncNode<ChSourceState> {
  public index: number = $state(0);
  public bias_voltage: number = $state(0);
  public activated: boolean = $state(false);
  public heading_text: string = $state("");
  public measuring: boolean = $state(false);

  public module_index: number;

  public temp: Array<number> = $state([0, 0, 0, 0]);
  public sign_temp = $state("+");
  public valid = $state(true);
  public editing = $state(false);
  public heading_editing = $state(false);
  public isHovering = $state(false);
  public focusing = $state(false);

  public integer = $derived(Math.round(Math.abs(this.bias_voltage * 1000)));
  public sign = $derived(this.bias_voltage < 0 ? "-" : "+");

  protected fields = this.defineFields<this>({
    index: { writable: false },
    bias_voltage: {
      blockWhen: () => this.editing,
      onBlocked: "queueLatest",
      validateRemote: (value) =>
        typeof value === "number" && value >= -5 && value <= 5,
      coerceRemote: (value) => Math.round(Number(value) * 10000) / 10000,
      onApplied: () => this.voltageToTemp(),
    },
    activated: {},
    heading_text: {
      blockWhen: () => this.heading_editing,
      onBlocked: "queueLatest",
      onApplied: () => this.voltageToTemp(),
    },
    measuring: {},
  });

  constructor(
    sync: SyncRuntime,
    path: string,
    data: ChSourceState,
    module_index: number,
  ) {
    super(sync, path);
    this.module_index = module_index;
    this.applySnapshot(data);
  }

  applySnapshot(data: ChSourceState) {
    this.index = data.index;
    this.bias_voltage = data.bias_voltage;
    this.activated = data.activated;
    this.heading_text = data.heading_text;
    this.measuring = data.measuring;
    this.voltageToTemp();
  }

  currentStateAsChange(): VsourceChange {
    return {
      module_index: this.module_index,
      index: this.index,
      bias_voltage: this.bias_voltage,
      activated: this.activated,
      heading_text: this.heading_text,
      measuring: this.measuring,
    };
  }

  async updateChannel(next: Partial<VsourceChange> = {}) {
    const requested = {
      ...this.currentStateAsChange(),
      ...next,
    };

    try {
      await this.sync.sendCommand("set_vsource_channel", requested);
      this.valid = true;
    } catch (error) {
      this.valid = false;
      throw error;
    }
  }

  finishEditing() {
    this.editing = false;
    this.sync.flushQueued(this, "bias_voltage");
  }

  finishHeadingEditing() {
    this.heading_editing = false;
    this.sync.flushQueued(this, "heading_text");
  }
}
```

Use `sendCommand()` for dbay channel updates rather than relying only on
`setVia`, because dbay commands usually update multiple fields and have hardware
side effects.

## Constructing Module Trees

Module constructors should pass stable JSON Pointer paths to children.

Example:

```ts
export class dac4D extends SvelteSyncNode<JsonModule> implements IModule {
  public core: CoreModule;
  public vsource: VsourceAddon;

  constructor(sync: SyncRuntime, path: string, data: JsonModule) {
    super(sync, path);
    this.core = new CoreModule(data.core);
    this.vsource = new VsourceAddon(
      sync,
      joinJsonPointer(path, "vsource"),
      data.core.slot,
      data.vsource?.channels,
      4,
    );
  }

  applySnapshot(data: JsonModule): void {
    this.core.update(data.core);
    if (data.vsource) {
      this.vsource.applySnapshot(data.core.slot, data.vsource.channels);
    }
  }
}
```

`VsourceAddon` should create channel nodes at:

```ts
joinJsonPointer(path, "channels", String(i))
```

For module replacement, dispose the old module subtree before replacing the
instance so stale path registrations do not remain:

```ts
system_state.data[i].dispose?.();
system_state.data[i] = new modules[nextType](syncRuntime, ptrForSlot, parsed.data[i]);
```

If dbay adds `dispose()`, have it recursively dispose child nodes too.

## Frontend Patch Handling In Phase 3

Once module classes are `SyncNode`s:

- Keep `syncRuntime.onSnapshot(...)` for initial hydration and reconnect
  recovery.
- Remove the Phase 2 `onPatch(() => updateSystemStatefromJson(runtime.snapshot()))`
  fallback.
- Let `SyncRuntime` route patches to registered nodes.

For structural patches, such as replacing an entire module at `/data/3`, the
registered module/root node should handle `applySnapshot()` or replacement
logic.

## Shared dac16D Updates

The `dac16D` linked-channel command should commit all affected channels in a
single backend transaction:

```python
with sync.transaction() as tx:
    for i, linked in enumerate(link_enabled):
        if not linked:
            continue
        source_channel = dac_16d.vsource.channels[i]
        source_channel.bias_voltage = canonical_voltage
        source_channel.activated = activated
        source_channel.heading_text = heading_text
        source_channel.measuring = measuring

        base = ptr("data", slot, "vsource", "channels", i)
        tx.set(ptr("data", slot, "vsource", "channels", i, "bias_voltage"), canonical_voltage)
        tx.set(ptr("data", slot, "vsource", "channels", i, "activated"), activated)
        tx.set(ptr("data", slot, "vsource", "channels", i, "heading_text"), heading_text)
        tx.set(ptr("data", slot, "vsource", "channels", i, "measuring"), measuring)
```

The frontend should receive one patch batch and one version.

## ADC / Sense Data

Use normal JSON Patch for low-rate state such as channel names, measuring flags,
and latest displayed voltage.

Use `lab-link` streams for high-rate time-series or continuous measurement
data. Do not push high-rate ADC sample arrays through the Pydantic state model.

Suggested split:

- `vsense.channels[i].measuring`: JSON Patch state.
- `vsense.channels[i].voltage`: JSON Patch if low-rate.
- live traces/history: `sync.stream(...)`.

## Error Display Rules For dbay

Backend `CommandError.display` should map to UI behavior:

- `banner`: persistent top-level warning/error. Use for hardware unavailable,
  UDP timeout, rack disconnected, command failed after retries.
- `toast`: transient notification. Use for invalid user input, wrong module
  type, rejected command.
- `inline`: attach to a specific path. Use for channel-level command failures
  or validation issues.

Backend `CommandError.path` should point to the most relevant node:

```python
ptr("data", module_index)
ptr("data", module_index, "vsource", "channels", index)
ptr("data", module_index, "vsource", "channels", index, "bias_voltage")
```

Frontend inline display should use the same path that the `SyncNode` was
registered with.

## Tests To Add In dbay

Backend tests:

- WebSocket snapshot returns current `global_state.system_state`.
- `initialize-module` updates REST response and broadcasts sync patch.
- `set_dac4d_vsource` success sends hardware command, updates state, broadcasts
  patch, and returns canonical result.
- Hardware return code failure sends `command_error` with `display: "banner"`.
- Wrong module type sends `command_error` with `display: "toast"`.
- `dac16D` shared update emits one patch batch and one version.

Frontend tests:

- App hydrates from sync snapshot without polling.
- Patch updates existing class-backed state.
- `bias_voltage` patch is queued while `editing` is true.
- Queued voltage patch flushes when editing ends.
- Command error goes to `syncErrors.banner`, `syncErrors.toasts`, or
  `syncErrors.byPath`.
- Module replacement disposes old sync nodes and creates new ones.

## Important Things Not To Do

- Do not replace dbay's class-backed state with plain `useSyncState()` as the
  final architecture. It is fine only as a temporary bridge.
- Do not commit backend state before hardware side effects succeed.
- Do not hand-build JSON Pointer strings in Python.
- Do not let incoming patches overwrite local UI-only fields.
- Do not remove REST endpoints until WebSocket commands have equivalent tests.
- Do not push high-rate sensor streams through JSON Patch state.

## Final Target Shape

Backend:

- `global_state.system_state` and `lab-link` state stay synchronized.
- New mutations are `@sync.command`s.
- Hardware failures raise `CommandError`.
- State commits happen through `sync.transaction()`.
- Structural changes use `sync.replace_state(...)` or explicit transactions.

Frontend:

- `App.svelte` connects once to `syncRuntime`.
- Initial snapshot hydrates module classes.
- Patches route to `SvelteSyncNode` instances.
- Channel edit fields use `blockWhen` and `queueLatest`.
- Commands use `syncRuntime.sendCommand(...)`.
- Hardware errors display through `syncErrors`.
