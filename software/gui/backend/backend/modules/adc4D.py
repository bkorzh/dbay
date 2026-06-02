from backend.addons.vsense import VsenseChange
from fastapi import Request
from fastapi import APIRouter, HTTPException
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.adc4D_spec import adc4D, adc4DController
from backend.sync import publish_vsense_channel, sync
from backend.util import identify_change
from lab_link import CommandContext, CommandError, ptr


logger = get_logger(__name__)

router = APIRouter(
    prefix="/adc4D",
    responses={404: {"description": "Not found"}},
)


def _command_error(
    code: str,
    message: str,
    *,
    path: str | None = None,
    display: str = "toast",
    severity: str = "warning",
) -> CommandError:
    return CommandError(
        code=code,
        message=message,
        display=display,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        path=path,
        recoverable=True,
    )


@sync.command
def set_adc4d_vsense(ctx: CommandContext, **params):
    change = VsenseChange(**params)

    try:
        module = cast(adc4D, global_state.system_state.data[change.module_index])
    except IndexError as exc:
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not an adc4D module.",
            path=ptr("data", change.module_index),
        ) from exc

    if module.core.type != "adc4D":
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not an adc4D module.",
            path=ptr("data", change.module_index),
        )

    if change.index < 0 or change.index > 4:
        raise _command_error(
            "invalid_channel_index",
            f"Channel {change.index} is outside the adc4D range.",
            path=ptr("data", change.module_index, "vsense"),
        )

    controller = cast(adc4DController, global_state.controllers[change.module_index])
    voltage = controller.readChannelVoltage(change.module_index, change.index) if change.measuring else 0.0

    sense_channel = module.vsense.channels[change.index]
    sense_channel.name = change.name
    sense_channel.measuring = change.measuring
    sense_channel.voltage = voltage
    change.voltage = voltage
    publish_vsense_channel(change.module_index, change.index)

    return change.model_dump(mode="json")




@router.put("/vsense/")
async def voltage_read(request: Request, change: VsenseChange):
    try:
        assert global_state.system_state.data[change.module_index].core.type == "adc4D" # type: ignore
    except AssertionError:
        logger.error("Module not adc4D")
        raise HTTPException(status_code=404, detail="Module not adc4D")
    
    slot = change.module_index
    assert slot == global_state.system_state.data[change.module_index].core.slot # type: ignore
    adc_4d = cast(adc4D, global_state.system_state.data[change.module_index]) # type: ignore
    
    identify_change(
        change, adc_4d.vsense.channels[change.index]
    )
    
    sense_channel = adc_4d.vsense.channels[change.index]
    sense_channel.name = change.name
    sense_channel.measuring = change.measuring
    adc4d_controller = cast(adc4DController, global_state.controllers[slot])

    try:
        assert (change.index >= 0 and change.index <= 4)
    except AssertionError:
        logger.error("Channel index not in 0-4 range")
        raise HTTPException(status_code=404, detail="Channel index not in 0-4 range")

    if change.measuring:
        logger.info(f"starting measurement on channel {change.index}")
        voltage = adc4d_controller.readChannelVoltage(slot, change.index)
        sense_channel.voltage = voltage
        logger.info(f"measured voltage: {voltage}V on channel {change.index}")
    else:
        logger.info(f"stopping measurement on channel {change.index}")
        sense_channel.voltage = 0.0

    change.voltage = sense_channel.voltage
    publish_vsense_channel(change.module_index, change.index)
    return change


@router.get("/read_channel/{channel}")
async def read_single_channel(channel: int, module_index: int):
    """Read voltage from a single ADC channel"""
    try:
        assert global_state.system_state.data[module_index].core.type == "adc4D" # type: ignore
    except (AssertionError, IndexError):
        logger.error("Module not adc4D or invalid module index")
        raise HTTPException(status_code=404, detail="Module not adc4D or invalid module index")
    
    if channel < 0 or channel > 4:
        logger.error(f"Channel {channel} out of range (0-4)")
        raise HTTPException(status_code=400, detail="Channel out of range (0-4)")
    
    adc4d_controller = cast(adc4DController, global_state.controllers[module_index])
    voltage = adc4d_controller.readChannelVoltage(module_index, channel)
    
    return {"channel": channel, "voltage": voltage}


@router.get("/read_all/")
async def read_all_channels(module_index: int):
    """Read voltages from all ADC channels"""
    try:
        assert global_state.system_state.data[module_index].core.type == "adc4D" # type: ignore
    except (AssertionError, IndexError):
        logger.error("Module not adc4D or invalid module index")
        raise HTTPException(status_code=404, detail="Module not adc4D or invalid module index")
    
    adc4d_controller = cast(adc4DController, global_state.controllers[module_index])
    voltages = adc4d_controller.readAllChannels(module_index)
    
    return {"voltages": voltages, "channels": list(range(5))}
