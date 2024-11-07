The `software` used for controlling the UDP-connected VME rack, is a full-stack web application built with [svelte](https://svelte.dev/) for the frontend, and [FastAPI](https://fastapi.tiangolo.com/) for the backend. Because the software is web based, the GUI can be accessed on most devices including smartphones, and could be accessed remotely with a proper VPN setup. 

### Architecture

Inside the `/frontend` folder, the web-based user interface is defined. By running a command in this folder, all code to operate this web-based software is compiled into several files which are placed in `/backend/dbay_control/`. The backend may then load and 'serve' this code. If you look inside the `package.json` file in `frontend`, you'll see that `npm run build` has been customized to compile the code with `vite build` and copy it to `/backend/snspd_bias_control/`. So anytime new frontend functionality is added and it's time to get it working with the backend, this command needs to be run.


>[!info] Deprecated
>### Frontend Development

The frontend code may be previewed and improved without interacting with the python backend. That is, the frontend is 'served' by node (a javascript runtime) instead of the the python backend. The only difference is that the frontend will load a dummy 'fallback state' that doesn't correspond to any state shared with the python backend.

node and npm need to be installed

```shell
cd frontend
npm install
npm run dev
```

Building the 'look' of a new module in the GUI is fastest by adding it to the fallback state located in `frontend/src/fallbackState.ts`, and watching for changes while the `npm run dev` development server is running.

>[!info] Deprecated
>#### Running the python server

Using `npm run dev` in the `/frontend` folder does not make use of the python backend at all. The 'backend' is needed to rout commands from the web browser to the hardware, and to be the official source of truth for the 'state' of the device bay system (what modules are plugged in, what voltages and channels are activated or powered, etc.)

If the frontend had been updated in some way, it will have to be recompiled by running `npm run build` in the frontend folder, thereby populating `/backend/snspd_bias_control/` with new html and javascript to serve.


Use anaconda or pip to install dependencies. For pip:

```bash
pip install --no-cache-dir --upgrade -r requirements.txt
cd backend
python main.py
```
## Development Process

To create the software for a new module, code in both `/frontend` and `/backend` must be added. This is an iterative process that often begins with defining what structs or data packets will be sent and received from what endpoints (e.g. `/dac16D/vsource/`). Here's some steps that don't necessarily need to happen in this order:

1. Create a new ui file `{module_name}.svelte` and core logic file `{module_name}_data.svelte.ts` in `frontend/src/lib/modules_dbay`. The `{module_name}_data.svelte.ts` may make use of the 'addon' classes defined in `frontend/src/lib/addons`. The `frontend/src/modules_day/index.svelte.ts` file must also be updated. Include the imports:

```ts
import { default as {module_name}_component } from './{module_name}.svelte'
import { {module_name} } from './{module_name}_data.svelte'
```

And add the new module/module_component to the `components` and `modules` objects defined below in the same file.
## Module data structure.

Module state is defined with a simple hierarchy of dataclasses (python) or objects (javascript/typescript). It's easiest to see the basic structure in `backend/state.py`

```python
class IModule(BaseModel):
core: Core
vsource: IVsourceAddon | None
vsense: IVsenseAddon | None
```

Both `IVsourceAddon` and `IVsenseAddon` contain a list of channels, each of which has a number of associated properties like `index`, `heading_text`, and `activated`.

2. Create a new python file in `backend/modules/` with name `{module_name}.py`. This python file may import datastructures from `backend/addons`. It must define a `router` using `APIRouter(prefix="/{module_name}", ...)` imported from `fastapi`. This router must also be imported into the `main.py` file (e.g. with `from .modules import {module_name}`), and 'connected' with the rest of the application using `app.include_router({module_name}.router)`.

NOTE: a library called `pydantic2ts` is used to transform the datastructures found in the addon files like `/backend/addons/vsource.py` to `interface.ts` files found in `frontend/src/lib/addons` (Note: I'm using a [fork](https://pypi.org/project/pydantic-to-typescript2/) of the original `pydantic2ts` library that supports pydantic >= 2.0). This ensures that the frontend and backend code agree on the 'shape' of data packets sent between them. If files like `/backend/addons/vsource.py` are changed, or new datastructures are defined for get/put requests, then `backend/pydantic_to_typescript.py` should be rerun and possibly updated. Because `pydantic2ts` converts from python to typescript, it makes sense to (1) get your data strucutres defined first in python with pydantic classes, (2) modify `backend/pydantic_to_typescript.py` to create a corresponding `interface.ts` file somewhere inside `frontend/`, and (3) work on the frontend code to use the datastructure from the newly modified/created `interface.ts` file.


>[!info] Deprecated
>## Docker Development Notes

*Commands and notes related to building the docker container*

The uploaded docker image was built on an ARM-based macbook. In order to build an image that will run on an x86-64 platform, you have to use `buildx`, a feature for multi-architecture builds.

```shell
# Create a new builder instance
docker buildx create --name mybuilder
# Switch to the new builder instance
docker buildx use mybuilder
# Start up the builder instance
docker buildx inspect --bootstrap
# build the image and pull it to the local docker desktop (?)
docker buildx build --platform linux/amd64 -t sansseriff/dbay . --load
```

Then with the docker desktop utility, publish the image to dockerhub. This way works without signing issues. If I used the --push option for that last command, then the built container had signing issues. I would get this error when trying to pull:

```shell
Trying to pull repository docker.io/sansseriff/dbay ...
missing signature key
```


