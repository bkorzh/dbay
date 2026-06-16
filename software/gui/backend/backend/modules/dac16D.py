from backend.addons.vsource import VsourceChange, SharedVsourceChange
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.dac16D_spec import dac16D, dac16DController
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


def _validated_change(params: dict) -> tuple[dac16D, VsourceChange]:
    change = VsourceChange(**params)

    try:
        module = cast(dac16D, global_state.system_state.data[change.module_index])
    except IndexError as exc:
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not a dac16D module.",
            path=ptr("data", change.module_index),
        ) from exc

    if module.core.type != "dac16D":
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not a dac16D module.",
            path=ptr("data", change.module_index),
        )

    if change.index < 0 or change.index > 15:
        raise _command_error(
            "invalid_channel_index",
            f"Channel {change.index} is outside the dac16D range.",
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

    return module, change


def _hardware_error(change: VsourceChange, detail: str) -> CommandError:
    return _command_error(
        "hardware_command_failed",
        "The dac16D voltage source command failed.",
        detail=detail,
        display="banner",
        severity="error",
        path=ptr("data", change.module_index, "vsource", "channels", change.index),
    )


def _validated_vsb_change(params: dict) -> tuple[dac16D, VsourceChange]:
    change = VsourceChange(**params)

    try:
        module = cast(dac16D, global_state.system_state.data[change.module_index])
    except IndexError as exc:
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not a dac16D module.",
            path=ptr("data", change.module_index),
        ) from exc

    if module.core.type != "dac16D":
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not a dac16D module.",
            path=ptr("data", change.module_index),
        )

    change.index = 0
    change.bias_voltage = round(change.bias_voltage, 4)
    if change.bias_voltage < -20 or change.bias_voltage > 20:
        raise _command_error(
            "voltage_out_of_range",
            f"{change.bias_voltage} V is outside the allowed VSB range.",
            path=ptr("data", change.module_index, "vsb", "bias_voltage"),
        )

    return module, change


@sync.command
def set_dac16d_vsource(ctx: CommandContext, **params):
    module, change = _validated_change(params)
    controller = cast(dac16DController, global_state.controllers[change.module_index])

    hardware_voltage = change.bias_voltage if change.activated else 0
    result = controller.setChVol(change.module_index, change.index, hardware_voltage)
    if result != 0:
        raise _hardware_error(change, f"setChVol returned {result}")

    source_channel = module.vsource.channels[change.index]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring
    source_channel.activated = change.activated
    source_channel.bias_voltage = change.bias_voltage

    return change.model_dump(mode="json")


@sync.command
def set_dac16d_vsource_shared(ctx: CommandContext, **params):
    shared_change = SharedVsourceChange(**params)
    module, change = _validated_change(shared_change.change.model_dump())
    controller = cast(dac16DController, global_state.controllers[change.module_index])

    changed_channels: list[int] = []
    for channel_index, linked in enumerate(shared_change.link_enabled[: len(module.vsource.channels)]):
        if not linked:
            continue

        hardware_voltage = change.bias_voltage if change.activated else 0
        result = controller.setChVol(change.module_index, channel_index, hardware_voltage)
        if result != 0:
            failed_change = change.model_copy(update={"index": channel_index})
            raise _hardware_error(failed_change, f"setChVol returned {result}")
        changed_channels.append(channel_index)

    for channel_index in changed_channels:
        source_channel = module.vsource.channels[channel_index]
        source_channel.heading_text = change.heading_text
        source_channel.measuring = change.measuring
        source_channel.activated = change.activated
        source_channel.bias_voltage = change.bias_voltage

    shared_change.change = change

    return shared_change.model_dump(mode="json")


@sync.command
def set_dac16d_vsb(ctx: CommandContext, **params):
    module, change = _validated_vsb_change(params)
    controller = cast(dac16DController, global_state.controllers[change.module_index])

    hardware_voltage = change.bias_voltage if change.activated else 0
    result = controller.setBias(hardware_voltage)
    if result != 0:
        raise _hardware_error(change, f"setBias returned {result}")

    module.vsb.heading_text = change.heading_text
    module.vsb.measuring = change.measuring
    module.vsb.activated = change.activated
    module.vsb.bias_voltage = change.bias_voltage

    return change.model_dump(mode="json")
