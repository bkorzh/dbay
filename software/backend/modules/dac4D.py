

from backend.addons.vsource import VsourceChange, ChSourceState
from backend.udp_control import UdpControl
from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException

from backend.location import BASE_DIR


import os
import csv
from datetime import datetime
from backend.initialize import global_controller

from backend.state import IModule, Core
from backend.addons.vsource import IVsourceAddon, ChSourceState

from typing import cast
from backend.logging import get_logger


from backend.initialize import system_state

from backend.modules.dac4D_spec import dac4D


logger = get_logger(__name__)

router = APIRouter(
    prefix="/dac4D",
    responses={404: {"description": "Not found"}},
)


class UDPdac4D:
    def __init__(self, udp: UdpControl):
        self.udp = udp

    def setDACVol(self, board: int, dacchan: int, voltage: float) -> str:
        message = ""
        if board <0 or board > 7:
            return "error, board out of range"
        if dacchan <0 or dacchan > 15:
            return "error, channel out of range"
        if  voltage < -10  or voltage > 10:
            return "error, voltage out of range"
        else:
            message = "SetDAC "+ str(board) + " " + str(dacchan) + " " + str(voltage) + "\n"
        
        return self.udp.send_message(message)

    def setChVol(self, board: int, diffchan: int, voltage: float):
        if board <0 or board > 7:
            logger.error("error, board out of range")
            return -1
        if diffchan <0 or diffchan > 7:
            logger.error("error, channel out of range")
            return -1
        if  voltage < -20  or voltage > 20:
            return "error, voltage out of range"
        else:
            r1 = self.setDACVol(board, diffchan*2, voltage/2)
            r2 = self.setDACVol(board, diffchan*2+1, -voltage/2)
            logger.debug(f"UDPdac4D: {r1}")
            logger.debug(f"UDPdac4D: {r2}")
            if r1 == '+ok\n' and r2 == '+ok\n':
                return 0
            else: 
                return -1
            

udp_dac4d = UDPdac4D(global_controller.udp_control)





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


@router.put("/vsource")
async def voltage_set(request: Request, change: VsourceChange):

    assert isinstance(system_state.data[change.module_index] , dac4D)
    dac_4d: dac4D = cast(dac4D, system_state.data[change.module_index])
    change.bias_voltage = round(change.bias_voltage, 4)


    identify_change(
        change, dac_4d.vsource.channels[change.index]
    )

    

    source_channel = dac_4d.vsource.channels[change.index]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring

    if change.index >= 0 and change.index <= 3:
        board = change.module_index

        assert board == system_state.data[change.module_index].core.slot

        if change.activated == False:
            logger.info(f"turning off {change.index} or already off")
            source_channel.bias_voltage = change.bias_voltage
            source_channel.activated = False
            udp_dac4d.setChVol(board, change.index, 0)
            logger.info(f"dac_4d.vsource.channels[change.index]: {dac_4d.vsource.channels[change.index]}")
            return change
        
        else:  # turning on or already on
            logger.info(f"turning on {change.index} or already on")
            source_channel.bias_voltage = change.bias_voltage
            if source_channel.activated == False:
                source_channel.activated = True
            udp_dac4d.setChVol(board, change.index, change.bias_voltage)
            return change
        

    else:
        raise HTTPException(status_code=404, detail="Channel not 1-4")
        