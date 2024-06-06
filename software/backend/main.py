import uvicorn
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# from fastapi import fastApi
from pydantic import BaseModel

from backend.modules import dac4D

from backend.logging import get_logger
logger = get_logger(__name__)

import asyncio
# import json

# import csv
# from datetime import datetime

from backend.initialize import UdpControl, global_controller, system_state
from backend.state import IModule, SystemState
# from backend.addons.vsource import IVsourceAddon
# from backend.addons.vsense import IVsenseAddon
from backend.location import BASE_DIR
from backend.modules import dac4D






class ModuleAddition(BaseModel):
    slot: int
    type: str
    # system_activated: bool




class VsourceParams(BaseModel):
    ipaddr: str
    timeout: float
    port: int
    dev_mode: bool





app = FastAPI()
app.include_router(dac4D.router)

##########
# 3 = 2
# important: you need to change how module_index is created (AND UPDATED) on the frontend. It should be the place in the array of the module. NOT the slot. 


app.mount(
    "/dbay_control/",
    StaticFiles(directory=Path(BASE_DIR, "dbay_control")),
    name="",
)




@app.get("/", response_class=HTMLResponse)
async def return_index(request: Request):
    return FileResponse(Path(BASE_DIR, "dbay_control", "index.html"))

    

async def zero_out_module(module: IModule):
    for channel in range(len(module.vsource.channels)):
        await asyncio.sleep(0.01)
        if not system_state.dev_mode: vsource.setChVol(module.slot, channel, 0)


# TODO
@app.post("/initialize-module")
async def init_module(request: Request, module_args: ModuleAddition):

    
    new_module = dac4D.create_prototype(module_args.slot)

    # Check if a module with the same slot already exists
    for i, module in enumerate(system_state.data):
        if module.core.slot == module_args.slot:
            # Replace the existing module
            system_state.data[i] = new_module
            break
    else:
        # Append the new module if no existing module was found
        system_state.data.append(new_module)

    # Zero out the new module
    asyncio.create_task(zero_out_module(new_module))

    system_state.data = sorted(system_state.data, key=lambda x: x.slot)
    return system_state


@app.post("/initialize-vsource")
async def vsource_set_state(params: VsourceParams):

    system_state.dev_mode = params.dev_mode

    global_controller.udp_control = UdpControl(params.ipaddr, params.port, params.dev_mode)

    logger.info("udp control re-initialized with params: {}".format(params.model_dump()))
    return params

@app.get("/full-state")
async def state():

    print(system_state.model_dump())

    return system_state


@app.put("/full-state")
async def state_set(request: Request, state: SystemState):
    logger.info("full state updated")
    global system_state
    system_state = state
    return system_state


if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--ipaddr', type=str, help='the voltage source ip address', default='10.7.0.162')
    # parser.add_argument('--timeout', type=int, help='timeout', 3)
    # parser.add_argument('--udp_remote', type=str, help='udp_remote', 5005)
    # parser.add_argument('--udp_local', type=str, help='udp_local', 55180)

    uvicorn.run(app, host="0.0.0.0", port=8000)
