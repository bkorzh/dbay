import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles

import multiprocessing
import mimetypes

from backend import server_api as _server_api_commands  # noqa: F401
from backend.modules import adc4D as _adc4D_commands  # noqa: F401
from backend.modules import dac16D as _dac16D_commands  # noqa: F401
from backend.modules import dac4D as _dac4D_commands  # noqa: F401
from backend.server_logging import get_logger
from backend.location import WEB_DIR
from backend.sync import restore_hardware_bindings, sync


logger = get_logger(__name__)
SERVE_PORT = 8345  # something a little random/unique
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")


# NOTE: if dev_mode is true and there's no VME rack to connect to, the fetch requests will take longer and there will be a
# hard to debug delay in the frontend!


@asynccontextmanager
async def lifespan(app: Starlette):
    async with sync.lifespan(app):
        restore_hardware_bindings()
        yield


# return the index.html file on browser
async def return_index(request: Request) -> FileResponse:
    return FileResponse(Path(WEB_DIR, "index.html"))


routes = [
    Route("/", return_index),
    WebSocketRoute("/sync/ws", sync.handle_ws),
    Mount("/assets", app=StaticFiles(directory=Path(WEB_DIR, "assets")), name="assets"),
]

origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "tauri://localhost",  # With this line, the Tauri app can now access the backend server
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = Starlette(routes=routes, middleware=middleware, lifespan=lifespan)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--ipaddr', type=str, help='the voltage source ip address', default='10.7.0.162')
    # parser.add_argument('--timeout', type=int, help='timeout', 3)
    # parser.add_argument('--udp_remote', type=str, help='udp_remote', 5005)
    # parser.add_argument('--udp_local', type=str, help='udp_local', 55180)
    multiprocessing.freeze_support()  # For Windows support
    uvicorn.run(app, host="0.0.0.0", port=SERVE_PORT)
