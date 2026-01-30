from backend.addons.vsense import VsenseChange
from fastapi import Request
from fastapi import APIRouter, HTTPException
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.adc4D_spec import adc4D, adc4DController
from backend.util import identify_change


logger = get_logger(__name__)

router = APIRouter(
    prefix="/adc4D",
    responses={404: {"description": "Not found"}},
)




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
