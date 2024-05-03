import uvicorn
import time
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates

# from fastapi import fastApi
from pydantic import BaseModel

from DACVME_ctrl import VMECTRL
from pathlib import Path
import asyncio
import json

import csv
from datetime import datetime

# !! use this to define the base directory because otherwise correct directories aren't found in docker
BASE_DIR = Path(__file__).resolve().parent


class Channel(BaseModel):
    index: int
    bias_voltage: float
    activated: bool
    heading_text: str
    measuring: bool


class Module(BaseModel):
    type: str
    slot: int
    name: str
    channels: list[Channel]


class VoltageChange(BaseModel):
    module_index: int
    index: int
    bias_voltage: float
    activated: bool
    heading_text: str
    measuring: bool


class ModuleAddition(BaseModel):
    slot: int
    type: str
    # system_activated: bool


class SourceState(BaseModel):
    data: list[Module]
    valid: bool
    dev_mode: bool

class VsourceParams(BaseModel):
    ipaddr: str
    timeout: float
    port: int
    dev_mode: bool


# load defuault ip address and port
with open(os.path.join(BASE_DIR, "vsource_params.json"), "r") as f:
    vsource_params = json.load(f)
    vsource = VMECTRL(vsource_params["ipaddr"], vsource_params["port"])


module_1 = Module(
    **{
        "type": "4Ch",
        "slot": 1,
        "name": "",
        "channels": [
            {
                "index": 1,
                "bias_voltage": 0.0,
                "activated": False,
                "heading_text": "server test 1",
                "measuring": False,
            },
            {
                "index": 2,
                "bias_voltage": 0.0,
                "activated": False,
                "heading_text": "server test 2",
                "measuring": False,
            },
            {
                "index": 3,
                "bias_voltage": 0.0,
                "activated": False,
                "heading_text": "server test 3",
                "measuring": False,
            },
            {
                "index": 4,
                "bias_voltage": 0.998,
                "activated": False,
                "heading_text": "server test 4",
                "measuring": False,
            },
        ],
    }
)

module_2 = Module(
    **{
        "type": "4Ch",
        "slot": 2,
        "name": "",
        "channels": [
            {
                "index": 1,
                "bias_voltage": 0.0,
                "activated": False,
                "heading_text": "server test 5",
                "measuring": False,
            },
            {
                "index": 2,
                "bias_voltage": 0.0,
                "activated": False,
                "heading_text": "server test 6",
                "measuring": False,
            },
            {
                "index": 3,
                "bias_voltage": 0.0,
                "activated": False,
                "heading_text": "server test 7",
                "measuring": False,
            },
            {
                "index": 4,
                "bias_voltage": 0.998,
                "activated": False,
                "heading_text": "server test 8",
                "measuring": False,
            },
        ],
    }
)


# data_state = [module_1, module_2]
data_state = []
system_activated = True


source_state = SourceState(data=data_state, valid=True, dev_mode=vsource_params["dev_mode"])

channel_default_state = {
    "index": 0,
    "bias_voltage": 0.0,
    "activated": False,
    "heading_text": "",
}

module_default_state = Module(
    type="4Ch",
    slot=0,
    name="",
    channels=[
        Channel(index=i, bias_voltage=0, activated=False, heading_text="", measuring=False)
        for i in range(4)
    ],
)


app = FastAPI()



app.mount(
    "/dbay_control",
    StaticFiles(directory=Path(BASE_DIR, "dbay_control")),
    name="dbay_control",
)


# templates = Jinja2Templates(directory=Path(BASE_DIR, "snspd_bias_control"))


# ## initialize Vsource
# source = isolatedVSource('10.7.0.162', 3, 5005, 55180)
# source.connect()


def write_state_to_csv(change: VoltageChange, changed_str):
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


def identify_change(change: VoltageChange, old_channel_state: Channel):
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

    board = source_state.data[change.module_index - 1].slot - 1

    change_strings = [
        f"Module index {module} (slot {board}), channel {index}: {key} changed from {old_value} to {new_value}"
        for key, (new_value, old_value) in diff.items()
    ]
    print("Changes: ", change_strings)
    return diff


@app.get("/", response_class=HTMLResponse)
async def return_index(request: Request):
    return FileResponse(Path(BASE_DIR, "dbay_control", "index.html"))


@app.put("/channel")
async def voltage_set(request: Request, change: VoltageChange):
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
        change, source_state.data[change.module_index - 1].channels[change.index - 1]
    )
    source_channel = source_state.data[change.module_index - 1].channels[
        change.index - 1
    ]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring

    if change.index >= 1 and change.index <= 4:

        # important! get the actual module slot. module.index is just an array index
        # "board" is 0 - 7, "slot" is 1 - 8
        board = source_state.data[change.module_index - 1].slot - 1

        if change.activated == False:
            print("turning off ", change.index, "or already off")
            source_channel.bias_voltage = change.bias_voltage
            source_channel.activated = False

            # !!!! update!

            if not source_state.dev_mode: vsource.setChVol(board, change.index-1, 0)
            return change
        else:  # turning on or already on
            print("turning on ", change.index-1, "or already on")
            source_channel.bias_voltage = change.bias_voltage

            if source_channel.activated == False:

                source_channel.activated = True

            # ch, voltage = source.setVoltage(change.channel, change.voltage)
            if not source_state.dev_mode: vsource.setChVol(board, change.index-1, change.bias_voltage)

            return change
    else:
        raise HTTPException(status_code=404, detail="Channel not 1-4")
    

async def zero_out_module(module: Module):
    for channel in range(len(module.channels)):
        await asyncio.sleep(0.01)
        if not source_state.dev_mode: vsource.setChVol(module.slot, channel, 0)


@app.post("/initialize-module")
async def state_set(request: Request, module_args: ModuleAddition):

    # system_activated = module_args.activated

    # I should submit all the default voltages to the VME when a new module is added
    new_module = Module(
        type=module_args.type,
        slot=module_args.slot,
        name="",
        channels=[
            Channel(index=i+1, bias_voltage=0, activated=False, heading_text="", measuring=False)
            for i in range(4)
        ],
    )

    # Check if a module with the same slot already exists
    for i, module in enumerate(source_state.data):
        if module.slot == module_args.slot:
            # Replace the existing module
            source_state.data[i] = new_module
            break
    else:
        # Append the new module if no existing module was found
        source_state.data.append(new_module)

    # Zero out the new module
    asyncio.create_task(zero_out_module(new_module))

    source_state.data = sorted(source_state.data, key=lambda x: x.slot)
    return source_state


@app.post("/initialize-vsource")
async def vsource_set_state(params: VsourceParams):

    source_state.dev_mode = params.dev_mode

    global vsource
    vsource = VMECTRL(params.ipaddr, params.port)
    print("source reinitialized")
    return params

@app.get("/full-state")
async def state():
    return source_state


@app.put("/full-state")
async def state_set(request: Request, state: SourceState):
    print("updating full state")
    global source_state
    source_state = state
    return source_state


if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--ipaddr', type=str, help='the voltage source ip address', default='10.7.0.162')
    # parser.add_argument('--timeout', type=int, help='timeout', 3)
    # parser.add_argument('--udp_remote', type=str, help='udp_remote', 5005)
    # parser.add_argument('--udp_local', type=str, help='udp_local', 55180)

    uvicorn.run(app, host="0.0.0.0", port=8000)
