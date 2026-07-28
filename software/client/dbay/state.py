"""Shared state schema for a DBay rack.

This is the single definition of what the GUI backend's authoritative state
looks like. The backend binds it to lab-link and mutates it; clients validate
the snapshot they receive against it. Previously each side maintained its own
copy and they drifted silently.

Models subclass :class:`lab_link.ReactiveModel`. On the backend those
assignments emit patch operations; on a client the node is not part of a bound
state tree, so writes are simply not recorded and the model behaves as an
ordinary validating pydantic model. One class therefore serves both sides.

Naming: ``*State`` suffixes distinguish these from the command-sending module
classes in :mod:`dbay.modules` — ``dbay.modules.dac4d.dac4D`` sends commands,
``dbay.state.Dac4DState`` describes state. The addon names (``ChSourceState``,
``IVsourceAddon``, ``ChSenseState``, ``IVsenseAddon``) are fixed: the GUI
frontend's generated TypeScript interfaces import them by name.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union, get_origin

from lab_link import ReactiveModel
from pydantic import (
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    WrapValidator,
)


__all__ = [
    "Core",
    "ModuleState",
    "IModule",
    "ChSourceState",
    "IVsourceAddon",
    "ChSenseState",
    "IVsenseAddon",
    "PollingState",
    "EmptyState",
    "Empty",
    "Dac4DState",
    "Dac16DState",
    "Adc4DState",
    "UnknownModuleState",
    "SystemState",
    "build_system_state_model",
    "BUILTIN_MODULE_STATES",
]


# --------------------------- module basics ---------------------------


class Core(ReactiveModel):
    """Identity of whatever occupies a slot."""

    slot: int
    type: str
    name: str


class ModuleState(ReactiveModel):
    """Base for every per-slot state model."""

    core: Core


# --------------------------- addons ---------------------------
# Names below are part of the frontend's generated TypeScript contract.


class ChSourceState(ReactiveModel):
    index: int
    bias_voltage: float
    activated: bool
    heading_text: str
    measuring: bool


class IVsourceAddon(ReactiveModel):
    channels: list[ChSourceState]


class ChSenseState(ReactiveModel):
    index: int
    voltage: float
    measuring: bool
    name: str


class IVsenseAddon(ReactiveModel):
    channels: list[ChSenseState]


class PollingState(ReactiveModel):
    """Polling configuration for modules that sample continuously."""

    running: bool = False
    frequency: float = 2.0  # Hz


# --------------------------- module states ---------------------------


class EmptyState(ModuleState):
    module_type: Literal["empty"] = "empty"
    core: Core


class Dac4DState(ModuleState):
    module_type: Literal["dac4D"] = "dac4D"
    core: Core
    vsource: IVsourceAddon


class Dac16DState(ModuleState):
    module_type: Literal["dac16D"] = "dac16D"
    core: Core
    vsource: IVsourceAddon
    vsb: ChSourceState
    vr: ChSenseState


class Adc4DState(ModuleState):
    module_type: Literal["adc4D"] = "adc4D"
    core: Core
    vsense: IVsenseAddon
    polling: PollingState = PollingState()


class UnknownModuleState(ModuleState):
    """Fallback for a module this build does not know about.

    A rack may contain modules newer than the consumer reading it, or ones
    registered only by a particular backend. Validating the whole snapshot
    would otherwise fail over a single unrecognized slot, so unknown entries
    land here instead: ``core`` is still typed, ``module_type`` is whatever the
    server reported, and every other field is preserved verbatim so nothing is
    lost for a consumer that does understand it.
    """

    model_config = ConfigDict(extra="allow")

    module_type: str
    core: Core


BUILTIN_MODULE_STATES: tuple[type[ModuleState], ...] = (
    EmptyState,
    Dac4DState,
    Dac16DState,
    Adc4DState,
)


# --------------------------- system state ---------------------------
#
# ``data`` cannot be ``list[ModuleState]``: the base declares fewer fields than
# the real modules and pydantic would validate the extra ones away. A tagged
# union on ``module_type`` is required to round-trip them intact.


def _module_annotation(module_states: tuple[type[ModuleState], ...]) -> Any:
    """Tagged union over ``module_states``, falling back to unknown modules."""
    known = TypeAdapter(
        Annotated[
            Union[module_states],  # type: ignore[valid-type]
            Field(discriminator="module_type"),
        ]
    )

    def _validate(value: Any, handler: Any) -> Any:
        # A discriminated union cannot express a catch-all member, so matching
        # is driven explicitly here: try the tagged union, and treat a failure
        # as "a module this build doesn't know about" rather than a bad payload.
        if isinstance(value, ModuleState):
            return value
        try:
            return known.validate_python(value)
        except ValidationError:
            return UnknownModuleState.model_validate(value)

    # The declared union *includes* UnknownModuleState so the serializer
    # recognizes it; without that, dumping a rack containing an unknown module
    # warns on every field. Validation never consults this union directly —
    # _validate owns that — but serialization dispatches on the instance type.
    return Annotated[
        Union[*module_states, UnknownModuleState],  # type: ignore[valid-type]
        WrapValidator(_validate),
    ]


def build_system_state_model(
    *extra_module_states: type[ModuleState],
    name: str = "SystemState",
) -> Any:
    """Build a ``SystemState`` whose ``data`` accepts ``extra_module_states`` too.

    The GUI backend registers its module models in a plugin registry, so the set
    of valid modules is a backend concern rather than a fixed property of the
    schema. It calls this with its registry; consumers needing only the
    built-ins can use :class:`SystemState` directly. Unknown module types fall
    back to :class:`UnknownModuleState` either way.
    """
    module_states = BUILTIN_MODULE_STATES + tuple(
        m for m in extra_module_states if m not in BUILTIN_MODULE_STATES
    )
    for model in module_states:
        # Checked here so a backend registering a module gets a direct answer
        # instead of pydantic's "needs field 'module_type' to be of type
        # `Literal`" raised from deep inside union construction.
        field = model.model_fields.get("module_type")
        if field is None or get_origin(field.annotation) is not Literal:
            raise TypeError(
                f"{model.__name__}.module_type must be a Literal (e.g. "
                f'Literal["my_module"]) so it can discriminate the module '
                "union; got "
                f"{field.annotation if field is not None else '<missing>'}."
            )
    annotation = _module_annotation(module_states)

    namespace: dict[str, Any] = {
        "__annotations__": {
            "data": list[annotation],  # type: ignore[valid-type]
            "valid": bool,
            "dev_mode": bool,
        },
    }
    return type(name, (ReactiveModel,), namespace)


SystemState = build_system_state_model()


# --------------------------- back-compat aliases ---------------------------
# Published from this module in 0.5.0 and earlier.

IModule = ModuleState
Empty = EmptyState
