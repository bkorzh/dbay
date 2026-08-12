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
from backend.modules import demoD as _demoD_commands  # noqa: F401
from backend.server_logging import get_logger
from backend.location import WEB_DIR
from backend.sync import restore_hardware_bindings, sync


logger = get_logger(__name__)
SERVE_PORT = 8345  # something a little random/unique
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")


# NOTE: dev_mode short-circuits UDP entirely (see udp_control.UDP.send_message):
# commands are acknowledged locally with "+ok" and nothing is sent. With
# dev_mode *off* and no VME rack to reach, every hardware command waits out UDP
# timeouts instead, which surfaces as a hard-to-debug delay in the frontend.


@asynccontextmanager
async def lifespan(app: Starlette):
    async with sync.lifespan(app):
        restore_hardware_bindings()
        yield


# return the index.html file on browser
async def return_index(request: Request) -> FileResponse:
    return FileResponse(Path(WEB_DIR, "index.html"))


# compiled_frontend/assets/ is a build artifact and is gitignored, so a fresh
# clone has none until `build.sh frontend` runs. StaticFiles refuses to serve a
# directory that does not exist — at import with check_dir=True, and on the first
# request otherwise — which would stop the backend from starting at all, and stop
# the tests from importing this module. Creating it empty keeps startup working
# and turns asset requests into ordinary 404s, which is the right answer during
# browser development because Vite serves the UI then. A packaged build always
# has the real files.
ASSETS_DIR = Path(WEB_DIR, "assets")
try:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
except OSError as exc:  # e.g. a read-only filesystem; check_dir=False covers it
    logger.warning("could not create %s: %s", ASSETS_DIR, exc)

routes = [
    Route("/", return_index),
    WebSocketRoute("/sync/ws", sync.handle_ws),
    Mount(
        "/assets",
        app=StaticFiles(directory=ASSETS_DIR, check_dir=False),
        name="assets",
    ),
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
