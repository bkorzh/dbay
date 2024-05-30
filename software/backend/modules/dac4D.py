

from addons.vsource import VsourceChange, ChSourceState
from DACVME_ctrl import VMECTRL
from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException

from ..state import system_state
from ..location import BASE_DIR

import os
import csv
from datetime import datetime
from ..initialize import vsource

router = APIRouter(
    prefix="/dac4D",
    responses={404: {"description": "Not found"}},
)


def write_state_to_csv(change: VsourceChange, changed_str):
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
    change_dict = change.dict()
    old_channel_state = old_channel_state.dict()
    module = change_dict["module_index"]
    index = change_dict["index"]
    del change_dict["module_index"]
    diff = {
        key: (value, old_channel_state.get(key))
        for key, value in change_dict.items()
        if old_channel_state.get(key) != value
    }
    diff.update(
        {
            key: (None, value)
            for key, value in old_channel_state.items()
            if key not in change_dict
        }
    )

    board = system_state.data[change.module_index - 1].module.slot - 1

    change_strings = [
        f"Module index {module} (slot {board}), channel {index}: {key} changed from {old_value} to {new_value}"
        for key, (new_value, old_value) in diff.items()
    ]
    print("Changes: ", change_strings)
    return diff


@router.put("/channel")
async def voltage_set(request: Request, change: VsourceChange):
    # print(
    #     "module:",
    #     change.module_index,
    #     "channel: ",
    #     change.index,
    #     " voltage: ",
    #     change.bias_voltage,
    #     " activated: ",
    #     change.activated,
    #     " heading_text: ",
    #     change.heading_text,
    #     " module_index: ",
    #     change.module_index,
    # )

    # change.index starts at 1
    change.bias_voltage = round(change.bias_voltage, 4)
    identify_change(
        change, system_state.data[change.module_index - 1].channels[change.index - 1]
    )
    source_channel = system_state.data[change.module_index - 1].channels[
        change.index - 1
    ]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring

    #
    #
    # important! check index. I changed the vsource addon to count from 0 index instead of 1.
    #
    #

    if change.index >= 1 and change.index <= 4:

        # important! get the actual module slot. module.index is just an array index
        # "board" is 0 - 7, "slot" is 1 - 8
        board = system_state.data[change.module_index - 1].slot - 1

        if change.activated == False:
            print("turning off ", change.index, "or already off")
            source_channel.bias_voltage = change.bias_voltage
            source_channel.activated = False

            # !!!! update!

            if not system_state.dev_mode: vsource.setChVol(board, change.index-1, 0)
            return change
        else:  # turning on or already on
            print("turning on ", change.index-1, "or already on")
            source_channel.bias_voltage = change.bias_voltage

            if source_channel.activated == False:

                source_channel.activated = True

            # ch, voltage = source.setVoltage(change.channel, change.voltage)
            if not system_state.dev_mode: vsource.setChVol(board, change.index-1, change.bias_voltage)

            return change
    else:
        raise HTTPException(status_code=404, detail="Channel not 1-4")