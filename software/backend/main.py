import uvicorn
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# from fastapi import fastApi
from pydantic import BaseModel

from backend.modules import dac4D
from backend.modules import dac16D
from typing import Literal, Union, Type, Any, Callable
from typing import cast
from backend.server_logging import get_logger
logger = get_logger(__name__)

import asyncio
import importlib

from backend.udp_control import parent_udp, UDP

# import csv
# from datetime import datetime

from backend.initialize import global_state
from backend.state import IModule, SystemState
# from backend.addons.vsource import IVsourceAddon
# from backend.addons.vsense import IVsenseAddon
from backend.location import BASE_DIR

# from state import load_modules_from_directory
# from importlib import import_module
# import os


import mimetypes
mimetypes.init()


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
app.include_router(dac16D.router)



app.mount(
    "/dbay_control/",
    StaticFiles(directory=Path(BASE_DIR, "dbay_control")),
    name="",
)




@app.get("/", response_class=HTMLResponse)
async def return_index(request: Request):
    mimetypes.add_type('application/javascript', '.js')
    return FileResponse(Path(BASE_DIR, "dbay_control", "index.html"))

    

async def zero_out_module(module: IModule):
    for channel in range(len(module.vsource.channels)):
        await asyncio.sleep(0.01)
        if not global_state.system_state.dev_mode: vsource.setChVol(module.slot, channel, 0)



@app.post("/initialize-module")
async def init_module(request: Request, addition_args: ModuleAddition):

    global_state.add_module(addition_args.type, addition_args.slot)
    
    return global_state.system_state


@app.post("/initialize-vsource")
async def vsource_set_state(params: VsourceParams):

    global_state.system_state.dev_mode = params.dev_mode
    udp = UDP(params.ipaddr, params.port, params.dev_mode)

    parent_udp.udp = udp

    logger.info("udp control re-initialized with params: {}".format(params.model_dump()))
    return params

@app.get("/full-state")
async def state():

    return global_state.system_state


@app.put("/full-state")
async def state_set(request: Request, state: SystemState):
    logger.info("full state updated")

    global_state.system_state = state
    return global_state.system_state


if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--ipaddr', type=str, help='the voltage source ip address', default='10.7.0.162')
    # parser.add_argument('--timeout', type=int, help='timeout', 3)
    # parser.add_argument('--udp_remote', type=str, help='udp_remote', 5005)
    # parser.add_argument('--udp_local', type=str, help='udp_local', 55180)

    uvicorn.run(app, host="0.0.0.0", port=8000)
