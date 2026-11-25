# How dbay uses lab-link to sync state

This document explains how the dbay GUI keeps a Python backend, a hardware
rack, and any number of connected web clients in agreement about the state of
the instrument — using the `lab-link` synchronization library.

It traces the **complete data lifecycle**: from clicking a chevron button to
nudge a channel voltage, through the command reaching the server, the hardware
write, the state mutation, and finally the broadcast that updates *every*
connected browser.

> **Repos involved**
> - dbay app: this repository (`software/gui/backend` + `software/gui/frontend`)
> - lab-link library: a *separate* repo at `/Users/andrew/Documents/PROGRAM_LOCAL/lab_link`.
>   Links below to `../lab_link/...` point there.

---

## 1. The mental model

lab-link is **server-authoritative**. There is exactly one source of truth: a
Pydantic model living in the Python backend. Browsers never own state — they
hold a *replica* and a *typed reactive view* of it.

The protocol has only four moving parts ([../lab_link/docs/index.md](../lab_link/docs/index.md)):

1. A browser connects over a WebSocket and receives a **snapshot** (the whole
   state plus a version number).
2. The browser sends **commands** (e.g. "set this voltage").
3. The server validates the command, performs side effects (talks to hardware),
   commits the new state, and bumps a **version** counter.
4. The server broadcasts a **JSON Patch** — a tiny diff describing exactly what
   changed — to *all* connected clients.

Clients never mutate authoritative state directly. They ask the server to do it
and then receive the resulting patch, *including the client that initiated the
change*. This is what keeps N browsers consistent: everybody applies the same
ordered stream of patches.

```
   ┌─────────────┐         command          ┌──────────────────┐      hardware
   │  Browser A  │ ───────────────────────► │   Python backend │ ────► VME rack
   │ (SyncNode)  │                          │   (LabSync)      │ ◄──── (UDP)
   └─────────────┘ ◄─── snapshot + patches ─│                  │
   ┌─────────────┐                          │  StateStore =    │
   │  Browser B  │ ◄─── patches ─────────────│  source of truth │
   └─────────────┘      (broadcast)          └──────────────────┘
```

Two key data shapes flow over the wire:

- **JSON Pointer** — a path into the state tree, e.g.
  `/data/2/vsource/channels/5/bias_voltage`. Built with `ptr(...)` on the
  backend and `joinJsonPointer(...)` on the frontend.
- **JSON Patch** ([RFC 6902](https://datatracker.ietf.org/doc/html/rfc6902)) —
  an array of ops like `{"op": "replace", "path": "/data/2/.../bias_voltage", "value": 1.25}`.

---

## 2. The two packages

lab-link ships as two aligned packages that share one protocol
([../lab_link/README.md](../lab_link/README.md)):

| Package | Where | What it provides |
|---|---|---|
| `lab-link` (PyPI) | [../lab_link/python/src/lab_link/](../lab_link/python/src/lab_link/) | FastAPI router, state store, command dispatcher, the `LabSync` object |
| `lab-link` (npm) | [../lab_link/js/src/](../lab_link/js/src/) | `SyncConnection` (transport), `SyncRuntime`/`SyncNode` (model layer), Svelte + React adapters |

dbay uses the FastAPI backend and the **Svelte adapter** from the JS side.

---

## 3. Backend: how the server owns state

### 3.1 Registering the state model

The single source of truth is a Pydantic model, `SystemState`
([software/gui/backend/backend/state.py](software/gui/backend/backend/state.py)),
registered with a `LabSync` instance in
[software/gui/backend/backend/sync.py:12-13](software/gui/backend/backend/sync.py#L12-L13):

```python
sync = LabSync()
sync.register_state(SystemState, initial=global_state.system_state)
```

`register_state` builds a `StateStore` around the model
([../lab_link/python/src/lab_link/core.py:97-118](../lab_link/python/src/lab_link/core.py#L97-L118)).
The `StateStore` ([../lab_link/python/src/lab_link/state_store.py](../lab_link/python/src/lab_link/state_store.py))
holds the validated state as a plain JSON-able dict, plus a monotonic
`_version` counter, guarded by a lock.

### 3.2 Wiring into FastAPI

In [software/gui/backend/backend/main.py](software/gui/backend/backend/main.py)
the app:

- imports each module's command file (`server_api`, `adc4D`, `dac16D`, `dac4D`)
  *for their side effects* — importing them runs the `@sync.command`
  decorators that register handlers
  ([main.py:13-16](software/gui/backend/backend/main.py#L13-L16)).
- mounts the sync router and runs `sync.lifespan(app)`
  ([main.py:31-43](software/gui/backend/backend/main.py#L31-L43)).

The WebSocket endpoint itself is declared in
[sync.py:18-20](software/gui/backend/backend/sync.py#L18-L20), delegating to
lab-link's `_handle_ws`. The server listens on port **8345**.

`lifespan` ([core.py:235-292](../lab_link/python/src/lab_link/core.py#L235-L292))
starts the `ConnectionManager`, recreates the patch queue in the running event
loop, and launches the background "drain" task and any `@sync.updater`
polling coroutines.

### 3.3 The connection handshake

When a browser opens the WebSocket, `_handle_ws`
([core.py:307-340](../lab_link/python/src/lab_link/core.py#L307-L340)):

1. generates a unique `client_id`,
2. grabs the current `snapshot()` and `version()` from the store,
3. calls `ConnectionManager.connect`, which **immediately sends a `snapshot`
   message** to that one client
   ([connection_manager.py:15-30](../lab_link/python/src/lab_link/connection_manager.py#L15-L30)),
4. then loops, reading JSON messages and dispatching `command` /
   `stream_resync` messages.

### 3.4 Commands: the only way to change state

A command is a decorated handler. dbay's voltage-set handler for the 16-channel
DAC lives in [software/gui/backend/backend/modules/dac16D.py:124-141](software/gui/backend/backend/modules/dac16D.py#L124-L141):

```python
@sync.command
def set_dac16d_vsource(ctx: CommandContext, **params):
    module, change = _validated_change(params)          # validate inputs
    controller = cast(dac16DController, global_state.controllers[change.module_index])

    hardware_voltage = change.bias_voltage if change.activated else 0
    result = controller.setChVol(change.module_index, change.index, hardware_voltage)  # talk to hardware
    if result != 0:
        raise _hardware_error(change, f"setChVol returned {result}")  # structured error

    source_channel = module.vsource.channels[change.index]
    source_channel.heading_text = change.heading_text   # mutate in-memory model
    source_channel.measuring = change.measuring
    source_channel.activated = change.activated
    source_channel.bias_voltage = change.bias_voltage
    publish_vsource_channel(change.module_index, change.index)  # broadcast the change

    return change.model_dump(mode="json")               # canonical result back to caller
```

Note the ordering, which is the heart of "server-authoritative":
**validate → hardware side effect → mutate model → publish patch → return result.**
If hardware fails, we raise *before* publishing, so no client ever sees a
voltage the rack didn't actually accept.

### 3.5 Dispatch, acks, and errors

`_dispatch_command` ([core.py:342-410](../lab_link/python/src/lab_link/core.py#L342-L410))
does the orchestration:

- looks up the handler by name; unknown command → `command_error`.
- sets a `CommandContext` (carrying `client_id`, `request_id`, `command`) into a
  `contextvar` so that any patch produced during the handler is tagged with who
  caused it.
- calls the handler (sync or async).
- waits for the patch queue to drain and pending broadcast tasks to flush, so
  the **patch is broadcast before the ack** — clients see the new value before
  the "your command succeeded" reply.
- sends a `command_ack` containing the new `version` and the handler's return
  value as `result`.
- on `CommandError`, sends a structured `command_error`
  ([core.py:434-451](../lab_link/python/src/lab_link/core.py#L434-L451)).

dbay raises display-ready `CommandError`s with severity/display hints — see the
helpers in [dac16D.py:18-35](software/gui/backend/backend/modules/dac16D.py#L18-L35)
and [dac16D.py:82-90](software/gui/backend/backend/modules/dac16D.py#L82-L90)
(`display="banner"` for hardware faults, `display="toast"` for validation).

### 3.6 Committing state and producing a patch

dbay mutates the plain Pydantic objects (`source_channel.bias_voltage = ...`)
and then calls a `publish_*` helper. Those helpers live in
[sync.py:31-105](software/gui/backend/backend/sync.py#L31-L105) and use a
**transaction** to batch several fields into one patch:

```python
def publish_vsource_channel(module_index: int, channel_index: int) -> None:
    module = global_state.system_state.data[module_index]
    channel = module.vsource.channels[channel_index]
    with sync.transaction() as tx:
        tx.set(ptr("data", module_index, "vsource", "channels", channel_index, "bias_voltage"), channel.bias_voltage)
        tx.set(ptr("data", module_index, "vsource", "channels", channel_index, "activated"),     channel.activated)
        tx.set(ptr("data", module_index, "vsource", "channels", channel_index, "heading_text"),  channel.heading_text)
        tx.set(ptr("data", module_index, "vsource", "channels", channel_index, "measuring"),      channel.measuring)
```

When the `with` block exits, `StateTransaction.__exit__`
([core.py:55-58](../lab_link/python/src/lab_link/core.py#L55-L58)) calls
`_commit_changes`, which:

1. applies all the changes into a *copy* of the state, re-validates it through
   Pydantic, swaps it in, and bumps the version
   ([state_store.py:46-64](../lab_link/python/src/lab_link/state_store.py#L46-L64)),
2. computes one JSON Patch via `jsonpatch.make_patch(old, new)`,
3. schedules a broadcast tagged with the `PatchMetadata`
   ([core.py:463-501](../lab_link/python/src/lab_link/core.py#L463-L501)).

One transaction = one validation = one version bump = one patch message. This
is why dbay uses transactions instead of four separate `sync.set(...)` calls.

> There are actually **two ways** state gets mutated in lab-link:
> - **Explicit API** (`sync.set`, `sync.transaction`, `sync.replace_state`) — what
>   dbay uses, called synchronously inside command handlers.
> - **Proxy writes** (`sync.state.x = 5`) — the `StateProxy`
>   ([../lab_link/python/src/lab_link/proxy.py](../lab_link/python/src/lab_link/proxy.py))
>   enqueues changes onto an async queue drained by `_drain_patch_queue`
>   ([core.py:513-538](../lab_link/python/src/lab_link/core.py#L513-L538)).
>   dbay doesn't really use this path; it prefers explicit `publish_*` helpers.

dbay also uses `replace_state` for whole-tree swaps (e.g. when a module is added
in [server_api.py:40-61](software/gui/backend/backend/server_api.py#L40-L61), via
`replace_sync_state()` in [sync.py:23-25](software/gui/backend/backend/sync.py#L23-L25)).

### 3.7 Broadcasting

`ConnectionManager.broadcast_patch`
([connection_manager.py:36-52](../lab_link/python/src/lab_link/connection_manager.py#L36-L52))
builds a `{"type": "patch", "patch": [...], "version": N, "originClientId": ...,
"requestId": ..., "command": ...}` message and sends it to **every** open socket.
The `originClientId`/`requestId`/`command` metadata lets each client tell
whether *it* caused the change.

---

## 4. Frontend: how the browser mirrors state

The frontend is split into three layers, mirroring lab-link's JS package
structure.

### 4.1 Transport — `SyncConnection`

[../lab_link/js/src/core/index.ts](../lab_link/js/src/core/index.ts) holds the
raw transport. `SyncConnection`:

- opens the WebSocket, auto-reconnects with exponential backoff
  ([core/index.ts:259-292](../lab_link/js/src/core/index.ts#L259-L292)),
- keeps a local replica `snapshotData` and the current `version`,
- on a `snapshot` message: clones it and fires `onSnapshot` handlers,
- on a `patch` message: **applies the patch to the local replica** with
  `applyPatch` and fires `onPatch` handlers
  ([core/index.ts:294-316](../lab_link/js/src/core/index.ts#L294-L316)),
- `sendCommand(command, params)` generates a `requestId`, sends the command, and
  returns a Promise that resolves on `command_ack` or rejects on `command_error`
  /timeout ([core/index.ts:195-237](../lab_link/js/src/core/index.ts#L195-L237)).

### 4.2 Model — `SyncRuntime` + `SyncNode`

[../lab_link/js/src/model/index.ts](../lab_link/js/src/model/index.ts) is the
clever layer. Plain JSON patches are fine, but dbay's UI is built from *classes
with methods and local UI state* (e.g. a channel that knows how to convert
voltage to a 4-digit display). `SyncNode` bridges the two.

- A `SyncNode` registers itself with the runtime at a JSON Pointer `path`
  ([model/index.ts:300-309](../lab_link/js/src/model/index.ts#L300-L309)).
- When a patch arrives, `SyncRuntime.routePatch` finds the **nearest registered
  node** for each op's path and hands it the *relative* sub-path
  ([model/index.ts:194-211](../lab_link/js/src/model/index.ts#L194-L211)).
- Each node declares a `fields` map (`defineFields`) describing **per-field
  policy** for how remote updates are applied
  ([model/index.ts:25-37](../lab_link/js/src/model/index.ts#L25-L37)).

The field policies are the most important concept for understanding dbay's UX:

| Policy | Meaning |
|---|---|
| `writable: false` | field is read-only locally; `setField` throws |
| `setVia: "cmd_name"` | writing this field sends a command instead of mutating locally |
| `blockWhen: () => bool` | if true, *reject incoming remote patches* for this field |
| `onBlocked: "drop" \| "queueLatest" \| fn` | what to do with a blocked patch |
| `validateRemote(v)` | reject patches whose value fails this check |
| `coerceRemote(v)` | transform an incoming value before applying |
| `onApplied(v)` | side effect after a remote value is applied |

`applyFieldPatch` ([model/index.ts:213-231](../lab_link/js/src/model/index.ts#L213-L231))
runs these in order: coerce → validate → check `blockWhen` → assign → `onApplied`.

### 4.3 Svelte adapter

[../lab_link/js/src/svelte/index.svelte.ts](../lab_link/js/src/svelte/index.svelte.ts)
re-exports `SyncNode` as **`SvelteSyncNode`** and provides `createSyncRuntime`.
Because dbay's node fields use Svelte 5 `$state(...)` runes, assigning to them
inside `applyFieldPatch` automatically triggers reactive UI updates — no manual
re-render needed.

dbay creates one shared runtime in
[software/gui/frontend/src/sync/runtime.svelte.ts](software/gui/frontend/src/sync/runtime.svelte.ts):

```ts
export const syncRuntime = createSyncRuntime<JsonSystemState>({
  url: backendWsUrl(),         // ws://127.0.0.1:8345/sync/ws (or same-host in prod)
  autoConnect: false,
  commandTimeoutMs: 10_000,
});
```

### 4.4 The dbay node tree

- [systemState.svelte.ts](software/gui/frontend/src/state/systemState.svelte.ts):
  `SystemStateClass extends SvelteSyncNode` at the root path `""`. It owns the
  top-level `valid` / `dev_mode` flags and the `data` array of modules.
- [vsource.svelte.ts](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts):
  `ChSourceStateClass extends SvelteSyncNode` is one channel, registered at
  `/data/<slot>/vsource/channels/<i>`. Its `fields` declaration
  ([vsource.svelte.ts:25-59](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts#L25-L59))
  is exactly where the editing-lock magic lives (see §6).
- [modules_dbay/index.svelte.ts](software/gui/frontend/src/lib/modules_dbay/index.svelte.ts):
  builds the class tree from a JSON snapshot (`createSystemStatefromJson`,
  [index.svelte.ts:151-166](software/gui/frontend/src/lib/modules_dbay/index.svelte.ts#L151-L166)),
  constructing each module/channel `SyncNode` at its proper JSON Pointer.

### 4.5 Connecting and the first snapshot

[App.svelte](software/gui/frontend/src/App.svelte) wires it all together on
mount ([App.svelte:53-98](software/gui/frontend/src/App.svelte#L53-L98)):

```ts
unsubSnapshot = syncRuntime.onSnapshot(({ data }) => {
  if (!didCreateState) { createSystemStatefromJson(data); didCreateState = true; }
  else                 { updateSystemStatefromJson(data); }
  // ...clear loading/fallback timers
});
unsubStatus  = syncRuntime.onStatus((status) => { /* loading UI */ });
unsubErrors  = syncRuntime.onCommandError((error) => syncErrors.add(error));
syncRuntime.connect();
```

So the first `snapshot` message *builds the entire class tree*; every later
`patch` is routed to the right node by `SyncRuntime`. If no snapshot arrives in
time, dbay falls back to a fake local state
([index.svelte.ts:193-216](software/gui/frontend/src/lib/modules_dbay/index.svelte.ts#L193-L216)).

---

## 5. The complete lifecycle: clicking a button to change a voltage

Here is the end-to-end story for the canonical case: a user bumps a dac16D
channel voltage up by 0.1 V.

### Step 1 — The click (browser, UI)

In [ChannelContent.svelte:49-63](software/gui/frontend/src/lib/ChannelContent.svelte#L49-L63),
clicking a chevron calls `increment(index, value)`. When *not* in edit mode it
computes a new voltage and calls `ch.validateUpdateVoltage(new_bias_voltage)`.

(There's also a typed-edit flow: clicking the digits sets `ch.editing = true`
([ChannelContent.svelte:164](software/gui/frontend/src/lib/ChannelContent.svelte#L164)),
the user types digits into `temp[]`, and `onSubmit` parses them — see
[vsource.svelte.ts:155-168](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts#L155-L168).
We'll come back to why edit mode matters in §6.)

### Step 2 — Build the change and call the command (browser, model)

`validateUpdateVoltage` clamps to ±5 V and calls `updateChannel`
([vsource.svelte.ts:143-190](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts#L143-L190)),
which assembles a `VsourceChange` and calls `onChannelChange` →
`requestChannelUpdate(data, "/vsource/")`.

`requestChannelUpdate` ([api.ts:36-38](software/gui/frontend/src/api.ts#L36-L38))
picks the right command name based on module type (`inferVsourceCommand`,
[api.ts:17-30](software/gui/frontend/src/api.ts#L17-L30)) — here
`set_dac16d_vsource` — and calls `sendCommand`
([api.ts:10-15](software/gui/frontend/src/api.ts#L10-L15)), which is just
`syncRuntime.sendCommand(...)`.

### Step 3 — Over the wire (transport)

`SyncConnection.sendCommand` sends
`{"type":"command","command":"set_dac16d_vsource","params":{...},"requestId":"<uuid>"}`
and parks a Promise keyed by `requestId`
([core/index.ts:195-237](../lab_link/js/src/core/index.ts#L195-L237)).

### Step 4 — Dispatch and hardware write (backend)

The server's `_handle_ws` receives the message and routes it to
`_dispatch_command` → `set_dac16d_vsource`
([dac16D.py:124-141](software/gui/backend/backend/modules/dac16D.py#L124-L141)).
The handler validates the params (`_validated_change`,
[dac16D.py:38-79](software/gui/backend/backend/modules/dac16D.py#L38-L79)),
then **calls the hardware**: `controller.setChVol(...)`. If that returns
nonzero, it raises a `CommandError(display="banner")` and *no patch is sent*.

### Step 5 — Mutate + publish (backend)

On success the handler writes the new values onto the in-memory Pydantic model
and calls `publish_vsource_channel(...)`
([sync.py:31-52](software/gui/backend/backend/sync.py#L31-L52)). The transaction
commits one patch, bumps the version, and schedules a broadcast tagged with the
originating `client_id`, `request_id`, and command name
([core.py:463-501](../lab_link/python/src/lab_link/core.py#L463-L501)).

### Step 6 — Broadcast to everyone (backend → all browsers)

`broadcast_patch` sends the `patch` message to **all** connected sockets
([connection_manager.py:36-52](../lab_link/python/src/lab_link/connection_manager.py#L36-L52)).
Then `_dispatch_command` waits for the broadcast to flush and sends a
`command_ack` (carrying the handler's `result` and the new `version`) back to
the originating browser only.

### Step 7 — Apply the patch (every browser)

In each browser, `SyncConnection.handleMessage` applies the patch to the local
JSON replica and fires `onPatch`
([core/index.ts:304-316](../lab_link/js/src/core/index.ts#L304-L316)).
`SyncRuntime.routePatch` finds the nearest node — the `ChSourceStateClass` at
`/data/<slot>/vsource/channels/<i>` — and calls `applyFieldPatch` for the
`bias_voltage` field
([model/index.ts:194-231](../lab_link/js/src/model/index.ts#L194-L231)).

For `bias_voltage`, the policy
([vsource.svelte.ts:27-37](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts#L27-L37)):
- `coerceRemote` rounds to 4 decimals,
- `validateRemote` checks it's a number,
- `blockWhen: () => this.editing` — if this user is *not* mid-edit, the value is
  assigned to the `$state` field,
- `onApplied` recomputes the 7-segment display (`voltageToTemp`) and runs the
  module `effect()`.

Because the field is a Svelte `$state`, assigning it re-renders the channel.

### Step 8 — Ack resolves the Promise (originating browser)

Back in the browser that clicked, the `command_ack` resolves the `sendCommand`
Promise, and `requestChannelUpdate` returns the canonical `VsourceChange`. The
calling code (`updateChannel`) also calls `setChannel(returnData)` to apply the
server's authoritative values directly
([vsource.svelte.ts:187-202](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts#L187-L202)).

**Net result:** the rack got the voltage, the originating browser shows it, and
every *other* connected browser updated via the broadcast patch — all from one
source of truth.

```
 click (chevron)                                                    other tabs
      │                                                                  ▲
      ▼                                                                  │ patch
 validateUpdateVoltage → updateChannel → requestChannelUpdate            │
      │ sendCommand("set_dac16d_vsource", {...})                         │
      ▼                                                                  │
 ── WebSocket ───────────────────────────────────────────────────────►  │
      │                                                                  │
 _dispatch_command → set_dac16d_vsource                                  │
      │ validate → controller.setChVol() → mutate model                  │
      ▼                                                                  │
 publish_vsource_channel  → transaction → StateStore.apply_values        │
      │ (version++, make JSON patch)                                     │
      ├── broadcast_patch ──► ALL sockets ─────────────────────────────►─┘
      └── command_ack ──► originating socket only
                              │
                              ▼
             Promise resolves; SyncRuntime.routePatch → applyFieldPatch
                              │
                              ▼
              $state bias_voltage updated → Svelte re-renders
```

---

## 6. Why "editing locks" matter (the subtle part)

Consider two users, or one user typing a new value while the backend's polling
loop pushes updates. Naively, an incoming patch could clobber the digits the
user is mid-way through typing. lab-link solves this with `blockWhen` +
`onBlocked`.

In [vsource.svelte.ts](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts):

- `bias_voltage` and `heading_text` declare `blockWhen: () => this.editing`
  (resp. `this.heading_editing`) with `onBlocked: "queueLatest"`
  ([vsource.svelte.ts:27-52](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts#L27-L52)).
- While the user is editing, incoming remote patches for that field are **not
  applied** — instead the latest one is stashed in a queue
  ([model/index.ts:252-273](../lab_link/js/src/model/index.ts#L252-L273)).
- When editing finishes, `finishEditing()` calls
  `this.sync.flushQueued(this, "bias_voltage")`
  ([vsource.svelte.ts:122-130](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts#L122-L130)),
  which replays the queued value if the lock is now clear
  ([model/index.ts:275-297](../lab_link/js/src/model/index.ts#L275-L297)).

So remote updates never fight the local editor, but they're not lost either —
the freshest one is applied the moment the user is done.

---

## 7. Error handling

Backend handlers raise `CommandError` with a `display` hint
([dac16D.py:18-35](software/gui/backend/backend/modules/dac16D.py#L18-L35)).
The transport rejects the `sendCommand` Promise *and* fires `onCommandError`
([core/index.ts:333-345](../lab_link/js/src/core/index.ts#L333-L345)). dbay's
[App.svelte:79-81](software/gui/frontend/src/App.svelte#L79-L81) feeds these into
[errors.svelte.ts](software/gui/frontend/src/sync/errors.svelte.ts), which sorts
them into a banner (hardware faults), per-path inline errors (validation on a
specific channel), or toasts.

Because the error is raised *before* `publish_*`, the rejected state never gets
broadcast — the UI shows the error but the authoritative state stays correct.

---

## 8. Quick reference — where to look

| I want to understand… | Look at |
|---|---|
| The whole protocol in one place | [../lab_link/docs/index.md](../lab_link/docs/index.md) |
| How the server owns/commits state | [../lab_link/python/src/lab_link/core.py](../lab_link/python/src/lab_link/core.py), [state_store.py](../lab_link/python/src/lab_link/state_store.py) |
| How patches reach all clients | [../lab_link/python/src/lab_link/connection_manager.py](../lab_link/python/src/lab_link/connection_manager.py) |
| dbay's state model | [software/gui/backend/backend/state.py](software/gui/backend/backend/state.py) |
| dbay's command handlers | [software/gui/backend/backend/modules/dac16D.py](software/gui/backend/backend/modules/dac16D.py), [server_api.py](software/gui/backend/backend/server_api.py) |
| dbay's publish helpers | [software/gui/backend/backend/sync.py](software/gui/backend/backend/sync.py) |
| Frontend transport | [../lab_link/js/src/core/index.ts](../lab_link/js/src/core/index.ts) |
| Frontend model/node layer | [../lab_link/js/src/model/index.ts](../lab_link/js/src/model/index.ts) |
| dbay's channel node + field policies | [software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts](software/gui/frontend/src/lib/addons/vsource/vsource.svelte.ts) |
| dbay's connect + snapshot wiring | [software/gui/frontend/src/App.svelte](software/gui/frontend/src/App.svelte), [runtime.svelte.ts](software/gui/frontend/src/sync/runtime.svelte.ts) |
| dbay's command-sending API | [software/gui/frontend/src/api.ts](software/gui/frontend/src/api.ts) |
</content>
</invoke>
