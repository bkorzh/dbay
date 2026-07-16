from backend.addons.vsource import VsourceChange
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.dac4D_spec import dac4D, dac4DController
from backend.sync import sync
from lab_link import CommandContext, CommandError, ptr


logger = get_logger(__name__)


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


@sync.command
def set_dac4d_vsource(ctx: CommandContext, **params):
    change = VsourceChange(**params)

    try:
        module = cast(dac4D, global_state.system_state.data[change.module_index])
    except IndexError as exc:
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not a dac4D module.",
            path=ptr("data", change.module_index),
        ) from exc

    if module.core.type != "dac4D":
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not a dac4D module.",
            path=ptr("data", change.module_index),
        )

    if change.index < 0 or change.index > 3:
        raise _command_error(
            "invalid_channel_index",
            f"Channel {change.index} is outside the dac4D range.",
            path=ptr("data", change.module_index, "vsource"),
        )

    change.bias_voltage = round(change.bias_voltage, 4)
    if change.bias_voltage < -5 or change.bias_voltage > 5:
        raise _command_error(
            "voltage_out_of_range",
            f"{change.bias_voltage} V is outside the allowed range.",
            path=ptr(
                "data",
                change.module_index,
                "vsource",
                "channels",
                change.index,
                "bias_voltage",
            ),
        )

    controller = cast(dac4DController, global_state.controllers[change.module_index])
    hardware_voltage = change.bias_voltage if change.activated else 0
    result = controller.setChVol(change.module_index, change.index, hardware_voltage)
    if result != 0:
        raise _command_error(
            "hardware_command_failed",
            "The dac4D voltage source command failed.",
            detail=f"setChVol returned {result}",
            display="banner",
            severity="error",
            path=ptr("data", change.module_index, "vsource", "channels", change.index),
        )

    source_channel = module.vsource.channels[change.index]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring
    source_channel.activated = change.activated
    source_channel.bias_voltage = change.bias_voltage

    return change.model_dump(mode="json")
        
