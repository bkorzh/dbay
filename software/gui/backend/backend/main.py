import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, Response
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


# Shown instead of a blank page when the frontend has never been built. The
# compiled frontend is not in git, so this is what a fresh clone sees if someone
# opens the backend's port directly.
NOT_BUILT_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Device Bay — frontend not built</title>
  <style>
    body { font-family: system-ui, sans-serif; line-height: 1.5; margin: 4rem auto;
           max-width: 34rem; padding: 0 1.5rem; color: #2d2d32; }
    h1 { font-size: 1.4rem; font-weight: 600; }
    code, pre { background: #f2f4f8; border-radius: 4px; }
    code { padding: 0.1rem 0.3rem; }
    pre { padding: 0.7rem 0.9rem; overflow-x: auto; }
    p { margin: 1rem 0; }
  </style>
</head>
<body>
  <h1>The frontend has not been built</h1>
  <p>The backend is running, but it has no compiled user interface to serve. The
  compiled frontend is a build artifact and is not kept in version control, so a
  fresh clone starts out without one.</p>
  <p>Build it once, from the repository root:</p>
  <pre>./software/gui/build.sh frontend</pre>
  <p>For day-to-day development you usually do not need this: run
  <code>./software/gui/dev-browser.sh</code> and open
  <a href="http://localhost:5173">localhost:5173</a>, where Vite serves the
  interface and reloads it as you edit.</p>
  <p>See <code>docs/content/Development/Start Here.md</code>.</p>
</body>
</html>
"""


# return the index.html file on browser
async def return_index(request: Request) -> Response:
    index = Path(WEB_DIR, "index.html")
    if not index.is_file():
        # 503 rather than 404: the route exists, the app just is not serveable yet.
        return HTMLResponse(NOT_BUILT_PAGE, status_code=503)
    return FileResponse(index)


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
