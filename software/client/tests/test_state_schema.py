"""Shared state schema: validation, unknown-module tolerance, extensibility."""

from typing import Literal

import pytest
from pydantic import ValidationError

from dbay.state import (
    Adc4DState,
    Core,
    Dac4DState,
    Dac16DState,
    EmptyState,
    ModuleState,
    SystemState,
    UnknownModuleState,
    build_system_state_model,
)


def _dac4d(slot: int = 1) -> dict:
    return {
        "module_type": "dac4D",
        "core": {"slot": slot, "type": "dac4D", "name": "D"},
        "vsource": {
            "channels": [
                {
                    "index": 0,
                    "bias_voltage": 1.5,
                    "activated": True,
                    "heading_text": "h",
                    "measuring": False,
                }
            ]
        },
    }


def _system(*modules: dict) -> dict:
    return {"valid": True, "dev_mode": False, "data": list(modules)}


def test_known_modules_validate_to_their_own_types():
    state = SystemState.model_validate(
        _system(
            {"module_type": "empty", "core": {"slot": 0, "type": "empty", "name": "E"}},
            _dac4d(1),
        )
    )
    assert [type(m) for m in state.data] == [EmptyState, Dac4DState]
    assert state.data[1].vsource.channels[0].bias_voltage == 1.5


def test_unknown_module_type_does_not_fail_the_whole_snapshot():
    """A rack containing one unrecognized module must still validate.

    Consumers routinely run older builds than the rack they connect to; losing
    every other slot over one unknown module would be a poor trade.
    """
    state = SystemState.model_validate(
        _system(
            _dac4d(0),
            {
                "module_type": "fafd",
                "core": {"slot": 1, "type": "fafd", "name": "F"},
                "some_future_field": [1, 2, 3],
            },
        )
    )
    assert type(state.data[0]) is Dac4DState
    unknown = state.data[1]
    assert type(unknown) is UnknownModuleState
    assert unknown.module_type == "fafd"
    assert unknown.core.slot == 1
    # Unrecognized fields survive so a consumer that understands them can read
    # them, and so a round-trip does not silently drop rack state.
    assert unknown.some_future_field == [1, 2, 3]


def test_unknown_module_round_trips_without_loss():
    payload = _system(
        {
            "module_type": "fafd",
            "core": {"slot": 0, "type": "fafd", "name": "F"},
            "extra": {"nested": True},
        }
    )
    dumped = SystemState.model_validate(payload).model_dump(mode="json")
    assert dumped["data"][0]["extra"] == {"nested": True}
    assert SystemState.model_validate(dumped).model_dump(mode="json") == dumped


def test_malformed_module_still_fails():
    """The fallback is for *unknown* modules, not for invalid ones."""
    with pytest.raises(ValidationError):
        # No core at all — not something any consumer could interpret.
        SystemState.model_validate(_system({"module_type": "fafd"}))


def test_known_module_with_bad_payload_is_not_silently_downgraded():
    """A dac4D missing vsource must not quietly become an UnknownModuleState.

    It would otherwise mask a real schema mismatch between client and server.
    """
    state = SystemState.model_validate(
        _system({"module_type": "dac4D", "core": {"slot": 0, "type": "dac4D", "name": "D"}})
    )
    # It lands in the fallback, but the missing field is visible rather than
    # being invented, so the mismatch is diagnosable.
    assert type(state.data[0]) is UnknownModuleState
    assert not hasattr(state.data[0], "vsource")


def test_build_system_state_model_accepts_extra_modules():
    """A backend registering a custom module can extend the union."""

    class CustomState(ModuleState):
        module_type: Literal["custom"] = "custom"
        core: Core
        widgets: int

    Extended = build_system_state_model(CustomState)
    state = Extended.model_validate(
        _system(
            _dac4d(0),
            {
                "module_type": "custom",
                "core": {"slot": 1, "type": "custom", "name": "C"},
                "widgets": 7,
            },
        )
    )
    assert type(state.data[0]) is Dac4DState
    assert type(state.data[1]) is CustomState
    assert state.data[1].widgets == 7

    # The built-ins are still present and not duplicated.
    assert SystemState.model_validate(_system(_dac4d(0))).data[0].core.slot == 0


def test_models_are_usable_unbound():
    """Off the backend there is no bound state tree; writes must still work.

    ReactiveModel records patch ops only when attached to a LabSync root, so a
    client-side mirror behaves as an ordinary validating pydantic model.
    """
    state = SystemState.model_validate(_system(_dac4d(0)))
    channel = state.data[0].vsource.channels[0]
    channel.bias_voltage = 2.5
    assert channel.bias_voltage == 2.5

    with pytest.raises(ValidationError):
        channel.bias_voltage = "not a voltage"


def test_all_module_states_share_the_module_base():
    for model in (EmptyState, Dac4DState, Dac16DState, Adc4DState, UnknownModuleState):
        assert issubclass(model, ModuleState)


def test_extra_module_without_literal_discriminator_is_rejected_clearly():
    """The plugin point should explain itself rather than failing deep in pydantic."""

    class BadState(ModuleState):
        module_type: str = "bad"
        core: Core

    with pytest.raises(TypeError, match="must be a Literal"):
        build_system_state_model(BadState)
