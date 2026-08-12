---
order: 5
---

# Adding a Module

What it takes to add support for a new hardware module, end to end. Read [[Architecture]] first — this page assumes you know what the bound state tree and commands are.

Use the existing `dac4D` as your reference implementation throughout: it is the smallest complete module. `dac16D` shows extra per-module fields, and `adc4D` shows continuous polling.

There are six places to touch, and forgetting any one of them produces a specific, recognizable failure — noted with each step.

## 1. Declare the state model

Module state models are shared between the backend and the Python client, so they live in `software/client/dbay/state.py`:

```python
class Dac4DState(ModuleState):
    module_type: Literal["dac4D"] = "dac4D"
    core: Core
    vsource: IVsourceAddon
```

`module_type` **must** be a `Literal`. It is the discriminator for the tagged union over module types, and `build_system_state_model` raises a `TypeError` naming your class if it is anything else.

Reuse the existing addons where they fit — `IVsourceAddon`, `IVsenseAddon`, `PollingState` — because the frontend already has matching components for them.

A rack containing a module type that a given build does not know about is not an error: unrecognized slots validate as `UnknownModuleState`, preserving their fields. That is what keeps an older Python client usable against a newer backend.

## 2. Optionally add a direct-mode client module

If the module should also be drivable without the GUI, add its ASCII command wrapper under `software/client/dbay/modules/<name>.py`, alongside `dac4d.py`, `adc4d.py`, and friends. The GUI's controller will delegate to it, so this is where the wire commands belong rather than in the backend.

## 3. Write the backend controller

Create `software/gui/backend/backend/modules/<name>_controller.py` with two things: a prototype factory, and a controller.

```python
def create_prototype(slot: int):
    channels = [ChSourceState(index=i, bias_voltage=0, activated=False,
                              heading_text="", measuring=False) for i in range(4)]
    return Dac4DState(core=Core(slot=slot, type="dac4D", name="my dac4D module"),
                      vsource=IVsourceAddon(channels=channels))


class dac4DController(Controller):
    def __init__(self, parent_udp: ParentUDP, module_slot: int):
        super().__init__(parent_udp, "DAC4D")
        self.module_slot = module_slot
        self._module = dbay_client.attach_module(module_slot, ClientDac4D)
        self.setDevice(self.module_slot)

    def setChVol(self, board: int, channel: int, voltage: float):
        ...
        return 0        # 0 on success, -1 on failure
```

`create_prototype` defines what a freshly initialized slot looks like. Note that `core.type` must be the same string as `module_type` — the backend discriminates on one and the frontend dispatches on the other.

Controller methods return status codes rather than raising, and the command handler turns a non-zero result into a user-visible error.

## 4. Register the module

Add an entry to `software/gui/backend/backend/module_registry.py`:

```python
REGISTERED_MODULES: dict[str, ModuleRegistration] = {
    ...
    "mymod": ModuleRegistration(
        model_class=MyModState,
        create_prototype=create_mymod,
        controller_class=myModController,
    ),
}
```

This is the only place the backend learns your module exists. `backend/state.py` rebuilds `SystemState` from the registry, so the state schema, initialization, and persistence all pick it up from here.

**If you skip this:** the module can never be initialized into a slot, and its state validates as `UnknownModuleState`.

## 5. Add command handlers

Create `software/gui/backend/backend/modules/<name>.py` for the write path:

```python
@sync.command
def set_mymod_output(ctx: CommandContext, **params):
    change = SomeChange(**params)
    module = cast(MyModState, global_state.system_state.data[change.module_index])

    if module.core.type != "mymod":
        raise _command_error("invalid_module", f"Slot {change.module_index + 1} is not a mymod.",
                             path=ptr("data", change.module_index))

    controller = cast(myModController, global_state.controllers[change.module_index])
    if controller.set_something(...) != 0:
        raise _command_error("hardware_command_failed", "The command failed.",
                             display="banner", severity="error")

    module.some_field = change.value      # this is what updates every connected UI
    return change.model_dump(mode="json")
```

The order matters: validate, talk to hardware, and only then mutate the state. The mutation is the broadcast — the return value is just an acknowledgement for the caller. Raise `CommandError` with a `path`, `display`, and `severity` so the frontend can place the error correctly (see [[Architecture]]).

Then import the module for its side effects in `backend/main.py`:

```python
from backend.modules import mymod as _mymod_commands  # noqa: F401
```

**If you skip this import:** the file is never executed, `@sync.command` never runs, and every call fails with an unknown-command error at runtime while the code looks perfectly correct.

## 6. Add the frontend

Three files under `software/gui/frontend/src/lib/modules_dbay/`:

**`<name>_data.svelte.ts`** — the mirrored state class, extending `SvelteSyncNode<JsonModule>` and bound to the slot's path:

```ts
export class mymod extends SvelteSyncNode<JsonModule> implements IModule {
  constructor(sync: SyncRuntime, path: string, data: JsonModule, replaceSelf?) {
    const nodePath = path ?? joinJsonPointer("", "data", String(parsed.core.slot));
    super(sync, nodePath);
    this.core = new CoreModule(parsed.core);
    this.vsource = new VsourceAddon(sync, joinJsonPointer(nodePath, "vsource"), ...);
  }
}
```

**`<name>.svelte`** — the UI, taking a `module_index` prop.

**`index.svelte.ts`** — register in both maps: `cc` (and `components`) for the Svelte component, and `modules` for the data-class constructor.

**If you skip the `modules` entry:** the backend happily reports a module in that slot and the frontend throws while constructing it, because it has no class for that type string.

## 7. Test it

Backend tests live in `software/gui/backend/tests/` and drive the app through Starlette's `TestClient` against a mock UDP server (`mock_udp_server.py`), so they exercise real command handling without hardware:

```bash
cd software/gui/backend && uv run pytest
```

Frontend integration tests live in `software/gui/frontend/src/tests/`:

```bash
cd software/gui/frontend && bun run test
```

`test_adc4d_polling.py` and `adc4D.integration.test.ts` are good models to copy for a new module.

## Checklist

- [ ] state model in `dbay/state.py`, with a `Literal` `module_type`
- [ ] optional direct-mode client module in `dbay/modules/`
- [ ] controller and `create_prototype` in `backend/modules/<name>_controller.py`
- [ ] entry in `backend/module_registry.py`
- [ ] `@sync.command` handlers in `backend/modules/<name>.py`, imported by `main.py`
- [ ] data class, component, and both registry entries on the frontend
- [ ] `core.type` and `module_type` strings identical everywhere
- [ ] tests on both sides

Documenting the module itself for users belongs in the [[Summary|Modules and Rack]] section rather than here.
