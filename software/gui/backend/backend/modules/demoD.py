"""Commands for the demoD tutorial module.

Two write paths: the voltage channel, which looks like every other vsource
module, and the trim slider, which is the simplest possible case — one float on
the module itself. See `docs/content/Development/Adding a Module.md`.

This file must be imported by `backend/main.py` for its decorators to run.
"""

from typing import cast

from lab_link import CommandContext, CommandError, ptr
from pydantic import BaseModel

from backend.addons.vsource import VsourceChange
from backend.initialize import global_state
from backend.modules.demoD_controller import (
    TRIM_MAX,
    TRIM_MIN,
    DemoDState,
    demoDController,
)
from backend.server_logging import get_logger
from backend.sync import sync


logger = get_logger(__name__)


class TrimChange(BaseModel):
    """Parameters for `set_demod_trim`."""

    module_index: int
    voltage: float


def _command_error(
    code: str,
    message: str,
    *,
    path: str | None = None,
    detail: str | None = None,
    display: str = "toast",
    severity: str = "warning",
) -> CommandError:
    return CommandError(
        code=code,
        message=message,
        detail=detail,
        display=display,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        path=path,
        recoverable=True,
    )


def _demod_at(module_index: int) -> DemoDState:
    """The demoD in a slot, or a command error explaining why there isn't one."""
    try:
        module = global_state.system_state.data[module_index]
    except IndexError as exc:
        raise _command_error(
            "invalid_module",
            f"Slot {module_index + 1} is outside the rack.",
            path=ptr("data", module_index),
        ) from exc

    if module.core.type != "demoD":
        raise _command_error(
            "invalid_module",
            f"Slot {module_index + 1} is not a demoD module.",
            path=ptr("data", module_index),
        )

    return cast(DemoDState, module)


@sync.command
def set_demod_vsource(ctx: CommandContext, **params):
    """Set the main output voltage — the same shape as the other vsource modules."""
    change = VsourceChange(**params)
    module = _demod_at(change.module_index)

    if change.index != 0:
        raise _command_error(
            "invalid_channel_index",
            "demoD has a single output channel.",
            path=ptr("data", change.module_index, "vsource"),
        )

    change.bias_voltage = round(change.bias_voltage, 4)
    if change.bias_voltage < -5 or change.bias_voltage > 5:
        raise _command_error(
            "voltage_out_of_range",
            f"{change.bias_voltage} V is outside the demoD range (-5 V to 5 V).",
            path=ptr(
                "data", change.module_index, "vsource", "channels", 0, "bias_voltage"
            ),
        )

    controller = cast(demoDController, global_state.controllers[change.module_index])
    # An output that is off should read its setpoint but drive zero.
    hardware_voltage = change.bias_voltage if change.activated else 0
    if controller.set_output_voltage(hardware_voltage) != 0:
        raise _command_error(
            "hardware_command_failed",
            "The demoD output command failed.",
            display="banner",
            severity="error",
            path=ptr("data", change.module_index, "vsource", "channels", 0),
        )

    # Only now, with the hardware in the requested state, does the shared state
    # change — and that mutation is what updates every connected client.
    channel = module.vsource.channels[0]
    channel.heading_text = change.heading_text
    channel.measuring = change.measuring
    channel.activated = change.activated
    channel.bias_voltage = change.bias_voltage

    return change.model_dump(mode="json")


@sync.command
def set_demod_trim(ctx: CommandContext, **params):
    """Set the trim voltage. Called by the slider, debounced by the frontend."""
    change = TrimChange(**params)
    module = _demod_at(change.module_index)

    voltage = round(change.voltage, 3)
    if voltage < TRIM_MIN or voltage > TRIM_MAX:
        raise _command_error(
            "trim_out_of_range",
            f"{voltage} V is outside the trim range ({TRIM_MIN} V to {TRIM_MAX} V).",
            display="inline",
            path=ptr("data", change.module_index, "trim_voltage"),
        )

    controller = cast(demoDController, global_state.controllers[change.module_index])
    if controller.set_trim_voltage(voltage) != 0:
        raise _command_error(
            "hardware_command_failed",
            "The demoD trim command failed.",
            display="banner",
            severity="error",
            path=ptr("data", change.module_index, "trim_voltage"),
        )

    module.trim_voltage = voltage

    return {"module_index": change.module_index, "voltage": voltage}
