import uvicorn
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import multiprocessing


# from fastapi import fastApi
from pydantic import BaseModel

from backend.modules import dac4D
from backend.modules import dac16D
from typing import Literal, Union, Type, Any, Callable
from typing import cast
from backend.server_logging import get_logger
from fastapi.middleware.cors import CORSMiddleware
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
from backend.location import BASE_DIR, WEB_DIR

# from state import load_modules_from_directory
# from importlib import import_module
import os
import signal

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

# NOTE: if dev_mode is true and there's no VME rack to connect to, the fetch requests will take longer and there will be a 
# hard to debug delay in the frontend! 





app = FastAPI()
app.include_router(dac4D.router)
app.include_router(dac16D.router)

origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "tauri://localhost", # this fixed it! With this line, the Tauri app can now access the FastAPI server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# app.mount(
#     "/",
#     StaticFiles(directory=Path(BASE_DIR, "dbay_control")),
#     name="static",
# )

# app.mount("/assets", StaticFiles(directory=Path(BASE_DIR, "dbay_control", "assets"), html=True), name="assets")
# app.mount("/assets", StaticFiles(directory=Path(BASE_DIR, "dbay_control", "assets")), name="static")
# app.mount("/", StaticFiles(directory=Path(BASE_DIR, "dbay_control", "assets"), html=True), name="")


# app.mount("/", StaticFiles(directory=Path(BASE_DIR, "dbay_control", "assets")), name="static")
# # Mount the parent directory at /files
# app.mount("/files", StaticFiles(directory=BASE_DIR), name="files")

# @app.get("/", response_class=HTMLResponse)
# async def return_index(request: Request):

#     # print("print(BASE_DIR): ", BASE_DIR)
#     mimetypes.add_type('application/javascript', '.js')
#     return FileResponse(Path(BASE_DIR, "dbay_control", "index.html"))

    # return FileResponse("/Users/andrew/Library/CloudStorage/OneDrive-Personal/PERSONAL/Programming/dbay/software/backend/backend/dbay_control/index.html")

    # app.mount("/", StaticFiles(directory=Path(BASE_DIR, "dbay_control", "")), name="")

    

# async def zero_out_module(module: IModule):
#     for channel in range(len(module.vsource.channels)):
#         await asyncio.sleep(0.01)
#         if not global_state.system_state.dev_mode: vsource.setChVol(module.slot, channel, 0)

# app.mount("/assets", StaticFiles(directory=Path(BASE_DIR, "dbay_control", "assets")), name="")

app.mount("/assets", StaticFiles(directory=Path(WEB_DIR, "assets")), name="")

@app.get("/", response_class=HTMLResponse)
async def return_index(request: Request):

    # print("print(BASE_DIR): ", BASE_DIR)
    mimetypes.add_type('application/javascript', '.js')
    # return FileResponse(Path(BASE_DIR, "dbay_control", "index.html"))
    return FileResponse(Path(WEB_DIR, "index.html"))



@app.get("/shutdown")
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return {"message": "Shutting down"}

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
    multiprocessing.freeze_support()  # For Windows support
    uvicorn.run(app, host="0.0.0.0", port=8000)
