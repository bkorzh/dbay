from backend.addons.vsource import VsourceChange
from fastapi import Request
from fastapi import APIRouter, HTTPException
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.dac4D_spec import dac4D, dac4DController
from backend.sync import publish_vsource_channel, sync
from backend.util import identify_change
from lab_link import CommandContext, CommandError, ptr


logger = get_logger(__name__)

router = APIRouter(
    prefix="/dac4D",
    responses={404: {"description": "Not found"}},
)


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
    publish_vsource_channel(change.module_index, change.index)

    return change.model_dump(mode="json")




@router.put("/vsource/")
async def voltage_set(request: Request, change: VsourceChange):
    try:
        assert global_state.system_state.data[change.module_index].core.type == "dac4D" # type: ignore
    except AssertionError:
        logger.error("Module not dac4D")
        raise HTTPException(status_code=404, detail="Module not dac4D")
    slot = change.module_index
    assert slot == global_state.system_state.data[change.module_index].core.slot # type: ignore
    dac_4d = cast(dac4D, global_state.system_state.data[change.module_index]) # type: ignore
    change.bias_voltage = round(change.bias_voltage, 4)
    identify_change(
        change, dac_4d.vsource.channels[change.index]
    )
    source_channel = dac_4d.vsource.channels[change.index]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring
    dac4d_controller = cast(dac4DController, global_state.controllers[slot])

    source_channel.activated = change.activated
    source_channel.bias_voltage = change.bias_voltage


    try:
        assert (change.index >= 0 and change.index <= 3)
    except AssertionError:
        logger.error("Channel index not in 0-3 range")
        raise HTTPException(status_code=404, detail="Channel index not in 0-3 range")


    if change.activated:
        logger.info(f"turning on {change.index} or already on")
        dac4d_controller.setChVol(slot, change.index, change.bias_voltage)
    else:  # turning on or already on
        logger.info(f"turning off {change.index} or already off")
        dac4d_controller.setChVol(slot, change.index, 0)
        logger.info(f"dac_4d.vsource.channels[change.index]: {dac_4d.vsource.channels[change.index]}")

    publish_vsource_channel(change.module_index, change.index)

    return change
        
