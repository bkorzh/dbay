import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import multiprocessing
import mimetypes

from backend import server_api as _server_api_commands  # noqa: F401
from backend.modules import adc4D as _adc4D_commands  # noqa: F401
from backend.modules import dac16D as _dac16D_commands  # noqa: F401
from backend.modules import dac4D as _dac4D_commands  # noqa: F401
from backend.server_logging import get_logger
from backend.location import WEB_DIR
from backend.sync import router as sync_router, sync


logger = get_logger(__name__)
SERVE_PORT = 8345  # something a little random/unique
mimetypes.init()


# NOTE: if dev_mode is true and there's no VME rack to connect to, the fetch requests will take longer and there will be a
# hard to debug delay in the frontend!


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with sync.lifespan(app):
        yield


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(sync_router)

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


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--ipaddr', type=str, help='the voltage source ip address', default='10.7.0.162')
    # parser.add_argument('--timeout', type=int, help='timeout', 3)
    # parser.add_argument('--udp_remote', type=str, help='udp_remote', 5005)
    # parser.add_argument('--udp_local', type=str, help='udp_local', 55180)
    multiprocessing.freeze_support()  # For Windows support
    uvicorn.run(app, host="0.0.0.0", port=SERVE_PORT)
