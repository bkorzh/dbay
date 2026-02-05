from backend.addons.vsource import VsourceChange, SharedVsourceChange
from backend.addons.vsense import ChSenseState
from fastapi import Request, WebSocket
from fastapi import APIRouter, HTTPException
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.dac16D_spec import dac16D, dac16DController
from backend.initialize import global_state
from backend.util import identify_change
import asyncio 
import random


logger = get_logger(__name__)

router = APIRouter(
    prefix="/dac16D",
    responses={404: {"description": "Not found"}},
)


@router.put("/vsource_shared/")
async def voltage_set_shared(request: Request, shared_change: SharedVsourceChange):
    try:
        assert global_state.system_state.data[shared_change.change.module_index].core.type == "dac16D" # type: ignore
    except AssertionError:
        logger.error("Module not dac16D")
        raise HTTPException(status_code=404, detail="Module not dac16D")
    
    slot = shared_change.change.module_index
    assert slot == global_state.system_state.data[shared_change.change.module_index].core.slot # type: ignore
    dac_16d = cast(dac16D, global_state.system_state.data[shared_change.change.module_index]) # type: ignore


    dac16d_controller = cast(dac16DController, global_state.controllers[slot])
    for i, boolean in enumerate(shared_change.link_enabled):
        source_channel = dac_16d.vsource.channels[i]

        if boolean:
            source_channel.heading_text = shared_change.change.heading_text
            source_channel.measuring = shared_change.change.measuring
            source_channel.bias_voltage = shared_change.change.bias_voltage
            source_channel.activated = shared_change.change.activated
            if source_channel.activated:
                dac16d_controller.setChVol(slot, i, shared_change.change.bias_voltage)
            else:
                dac16d_controller.setChVol(slot, i, 0)

    return shared_change

@router.put("/vsb/")
async def voltage_set_vsb(request: Request, change: VsourceChange):
    pass


@router.websocket("/ws_vsense/")
async def websocket_vsense_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        number = random.randint(0, 100)/100
        logger.info(f"Received data: {number}")
        vsense_state = ChSenseState(index=0, voltage=number, measuring=True, name="dac16D vr")
        await websocket.send_text(vsense_state.model_dump_json())
        await asyncio.sleep(0.1)

@router.put("/vsource/")
async def voltage_set(request: Request, change: VsourceChange):
    try:
        assert global_state.system_state.data[change.module_index].core.type == "dac16D" # type: ignore
    except AssertionError:
        logger.error("Module not dac16D")
        raise HTTPException(status_code=404, detail="Module not dac16D")
    slot = change.module_index
    assert slot == global_state.system_state.data[change.module_index].core.slot # type: ignore
    dac_16d = cast(dac16D, global_state.system_state.data[change.module_index]) # type: ignore
    change.bias_voltage = round(change.bias_voltage, 4)
    identify_change(
        change, dac_16d.vsource.channels[change.index]
    )
    source_channel = dac_16d.vsource.channels[change.index]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring
    dac16d_controller = cast(dac16DController, global_state.controllers[slot])
    source_channel.activated = change.activated
    source_channel.bias_voltage = change.bias_voltage


    try:
        assert (change.index >= 0 and change.index <= 15)
    except AssertionError:
        logger.error("Channel index not in 0-3 range")
        raise HTTPException(status_code=404, detail="Channel index not in 0-3 range")
    

    logger.info(f"change.index: {change.index}")
    if change.activated:
        logger.info(f"turning on {change.index} or already on")
        dac16d_controller.setChVol(slot, change.index, change.bias_voltage)
    else:  # turning on or already on
        logger.info(f"turning off {change.index} or already off")
        dac16d_controller.setChVol(slot, change.index, 0)
        logger.info(f"dac_4d.vsource.channels[change.index]: {dac_16d.vsource.channels[change.index]}")

    return change


