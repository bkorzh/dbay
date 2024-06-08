

from backend.addons.vsource import VsourceChange, ChSourceState
from fastapi import Request
from fastapi import APIRouter, HTTPException

from backend.location import BASE_DIR


import os
import csv
from datetime import datetime
from backend.initialize import global_state

from backend.addons.vsource import ChSourceState

from typing import cast
from backend.logging import get_logger

from backend.modules.dac4D_spec import dac4D, dac4DController


from backend.initialize import global_state


logger = get_logger(__name__)

router = APIRouter(
    prefix="/dac4D",
    responses={404: {"description": "Not found"}},
)




def write_state_to_csv(change: VsourceChange, changed_str: str):
    with open(os.path.join(BASE_DIR, "log.csv"), "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                datetime.now(),
                changed_str,
                change.index,
                change.bias_voltage,
                change.activated,
                change.heading_text,
                change.module_index,
            ]
        )

def identify_change(change: VsourceChange, old_channel_state: ChSourceState):
    change_dict = change.model_dump()
    old_channel_state_dict = old_channel_state.model_dump()
    module = change_dict["module_index"]
    index = change_dict["index"]
    del change_dict["module_index"]
    diff = {
        key: (value, old_channel_state_dict.get(key))
        for key, value in change_dict.items()
        if old_channel_state_dict.get(key) != value
    }
    diff.update(
        {
            key: (None, value)
            for key, value in old_channel_state_dict.items()
            if key not in change_dict
        }
    )
    board = change.module_index

    change_strings = [
        f"Module index {module} (slot {board}), channel {index}: {key} changed from {old_value} to {new_value}"
        for key, (new_value, old_value) in diff.items()
    ]
    logger.info(f"Changes: {change_strings}")
    return diff


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

    if change.index >= 0 and change.index <= 3:
        

        

        if change.activated == False:
            logger.info(f"turning off {change.index} or already off")
            source_channel.bias_voltage = change.bias_voltage
            source_channel.activated = False
            
            
            dac4d_controller.setChVol(slot, change.index, 0)

            logger.info(f"dac_4d.vsource.channels[change.index]: {dac_4d.vsource.channels[change.index]}")
            return change
        
        else:  # turning on or already on
            logger.info(f"turning on {change.index} or already on")
            source_channel.bias_voltage = change.bias_voltage
            if source_channel.activated == False:
                source_channel.activated = True

            dac4d_controller.setChVol(slot, change.index, change.bias_voltage)
            return change
        

    else:
        raise HTTPException(status_code=404, detail="Channel not 1-4")
        