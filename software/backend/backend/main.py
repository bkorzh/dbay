import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import multiprocessing
import socket
from pydantic import BaseModel
import psutil
import os
import signal
import mimetypes

from backend.modules import dac4D
from backend.modules import dac16D
from backend.server_logging import get_logger
from backend.udp_control import parent_udp, UDP
from backend.initialize import global_state
from backend.state import SystemState
from backend.location import WEB_DIR


logger = get_logger(__name__)
SERVE_PORT = 8345  # something a little random/unique
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


class ServerInfo(BaseModel):
    ipaddr: str
    port: int


# NOTE: if dev_mode is true and there's no VME rack to connect to, the fetch requests will take longer and there will be a
# hard to debug delay in the frontend!


app = FastAPI()
app.include_router(dac4D.router)
app.include_router(dac16D.router)

origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "tauri://localhost",  # With this line, the Tauri app can now access the FastAPI server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/assets", StaticFiles(directory=Path(WEB_DIR, "assets")), name="")


# return the index.html file on browser
@app.get("/", response_class=HTMLResponse)
async def return_index(request: Request):
    mimetypes.add_type("application/javascript", ".js")
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

    logger.info(
        "udp control re-initialized with params: {}".format(params.model_dump())
    )
    return params


@app.get("/full-state")
async def state():
    return global_state.system_state


@app.put("/full-state")
async def state_set(request: Request, state: SystemState):
    logger.info("full state updated")

    global_state.system_state = state
    return global_state.system_state


@app.get("/server-info")
async def server_info():
    hostname = socket.gethostname()

    # Get the actual IP address using psutil
    ipaddr = "127.0.0.1"
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                ipaddr = addr.address
                break
        if ipaddr != "127.0.0.1":
            break

    port = SERVE_PORT  # The port your server is running on

    return ServerInfo(ipaddr=ipaddr, port=port)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--ipaddr', type=str, help='the voltage source ip address', default='10.7.0.162')
    # parser.add_argument('--timeout', type=int, help='timeout', 3)
    # parser.add_argument('--udp_remote', type=str, help='udp_remote', 5005)
    # parser.add_argument('--udp_local', type=str, help='udp_local', 55180)
    multiprocessing.freeze_support()  # For Windows support
    uvicorn.run(app, host="0.0.0.0", port=SERVE_PORT)
