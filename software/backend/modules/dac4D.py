

from backend.addons.vsource import VsourceChange, ChSourceState
from backend.DACVME_ctrl import VMECTRL
from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException

from backend.state import system_state
from backend.location import BASE_DIR

import os
import csv
from datetime import datetime
from backend.initialize import vsource

from backend.state import system_state, IModule, Core, SystemState
from backend.addons.vsource import IVsourceAddon, ChSourceState

router = APIRouter(
    prefix="/dac4D",
    responses={404: {"description": "Not found"}},
)




def create_prototype(slot: int) -> IModule:

    channels = [ChSourceState(index=i, bias_voltage=0, activated=True, heading_text=f"{i}th ch dac4D", measuring=False) for i in range(4) ]

    dac4D_prototype = IModule(core=Core(slot=slot, type="dac4D", name="my dac4D"), vsource=IVsourceAddon(channels=channels))

    return dac4D_prototype

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

    # board = system_state.data[module - 1].core.slot - 1
    board = change.module_index

    change_strings = [
        f"Module index {module} (slot {board}), channel {index}: {key} changed from {old_value} to {new_value}"
        for key, (new_value, old_value) in diff.items()
    ]
    print("Changes: ", change_strings)
    return diff


@router.put("/vsource")
async def voltage_set(request: Request, change: VsourceChange):

    change.bias_voltage = round(change.bias_voltage, 4)
    identify_change(
        change, system_state.data[change.module_index].vsource.channels[change.index]
    )
    source_channel = system_state.data[change.module_index].vsource.channels[change.index]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring

    #
    #
    # important! check index. I changed the vsource addon to count from 0 index instead of 1.
    #
    #

    if change.index >= 0 and change.index <= 3:

        # important! get the actual module slot. module.index is just an array index
        # "board" is 0 - 7, "slot" is 1 - 8

        board = change.module_index

        assert board == system_state.data[change.module_index].core.slot
        # board = system_state.data[change.module_index - 1].slot - 1


        # print("system state dev mode: ", system_state.dev_mode)

        if change.activated == False:
            print("turning off ", change.index, "or already off")
            source_channel.bias_voltage = change.bias_voltage
            source_channel.activated = False

            

            if not system_state.dev_mode: vsource.setChVol(board, change.index, 0)

            print(source_channel)
            print(system_state.data[change.module_index].vsource.channels[change.index])
            return change
        else:  # turning on or already on
            print("turning on ", change.index, "or already on")
            source_channel.bias_voltage = change.bias_voltage

            print("what??")
            if source_channel.activated == False:

                source_channel.activated = True

            # ch, voltage = source.setVoltage(change.channel, change.voltage)
            if not system_state.dev_mode: vsource.setChVol(board, change.index, change.bias_voltage)
            print("what who")
            print(source_channel)
            print(system_state.data[change.module_index].vsource.channels[change.index])

            return change
        

    else:
        raise HTTPException(status_code=404, detail="Channel not 1-4")