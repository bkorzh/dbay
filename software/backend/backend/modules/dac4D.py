from backend.addons.vsource import VsourceChange
from fastapi import Request
from fastapi import APIRouter, HTTPException
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.dac4D_spec import dac4D, dac4DController
from backend.util import identify_change


logger = get_logger(__name__)

router = APIRouter(
    prefix="/dac4D",
    responses={404: {"description": "Not found"}},
)




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


    return change
        