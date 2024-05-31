# d-bay software: FRONTEND and BACKEND

A web-app user interface for controlling an UDP connected isolated voltage source, built with [svelte](https://svelte.dev/) for the frontend, and [FastAPI](https://fastapi.tiangolo.com/) for the backend. 


![UI](https://raw.githubusercontent.com/sansseriff/Isolated_Voltage_Source/master/vsource_cropped_dark.png#gh-dark-mode-only)
![UI](https://raw.githubusercontent.com/sansseriff/Isolated_Voltage_Source/master/vsouce_cropped_light.png#gh-light-mode-only)


## Installation
<details>
<summary>How to set up the DBay graphical user interface for use in your lab</summary>


### 1. Install docker

#### Red Hat Enterprise Linux (RHEL) 7.X
RHEL7 needs some additional steps prior to installing Docker CE Engine.

1. Add the docker community edition repo

    ```console
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    ```

2. Edit repo to add centos (centos is the open source free version of RHEL, at least up until RHEL 8)

    Edit the `/etc/yum.repos.d/docker-ce.repo`, for example using nano with the command:

    ```console
    sudo nano /etc/yum.repos.d/docker-ce.repo
    ```

    Add the following to the top or bottom of the file:
    ```
    [centos-extras]
    name=Centos extras - $basearch
    baseurl=http://mirror.centos.org/centos/7/extras/x86_64
    enabled=1
    gpgcheck=0
    ```

    Save the file, and run `sudo yum update`

    Now, you should be able to run `sudo yum install docker`. 

3. Without extra configuration, all docker commands will need to be prefaced with `sudo`. For example, `docker ps` becomes `sudo docker ps`

4. After installation, you may need to start the docker daemon:
    ```
    sudo systemctl start docker
    ```

#### Red Hat Enterprise Linux (RHEL) 8 - untested

The above guide for RHEL may work, with the baseurl in `[centos-extras]` changed to `https://mirror.centos.org/centos/8/extras/x86_64/`. Also or alteratively, [this](https://docs.docker.com/engine/install/centos/) guide may work. 

#### Ubuntu

follow [this](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04) guide for installation, and for configuring docker commands to work without sudo. 

### 2a. Download and run published image
If you don't plan to customize the voltage source user interface or back-end webserver, you may download a version from dockerhub. This version works on x86-64 architecture computers. It will not work on ARM-based computers like raspberry pi. To get an ARM-compatible image, you will have to build it yourself. See instructions in 2b. 

Download:

```
docker pull sansseriff/vsource_control
```

Run:
```
docker run -d --restart unless-stopped --name vsource_control_container --log-opt max-size=10m --log-opt max-file=3 -p 80:80 sansseriff/vsource_control
```

The user interface should now be visible by typing `0.0.0.0` into the browser of the computer running docker. If docker was installed on a remote host computer on the same network, view the UI by directing the browser to the ip address of the host computer. 

### 2b. Clone github repo and build container
If you need to customize the user interface or webserver, clone this repository, and rebuild the container:

```
git clone https://github.com/sansseriff/Isolated_Voltage_Source.git
```

You may customize backend python code in the `backend/` directory. 

In order to customize and rebuild the frontend javascript and html, you will need to have `node` installed. Inside the `frontend/` folder, run `npm install` to install all the necessary libraries needed to work with svelte. Running `npm run build`, will rebuild the frontend to vanilla javascript & html and place it in `backend/snspd_bias_control/` where the python backend webserver will find it. 

When the code is ready to go, run this command in the root directory to build the container, using the instructions present in the local `Dockerfile`; 

```
docker build -t vsource_control .
```

Then run the built container image:

```
docker run -d --restart unless-stopped --name vsource_control_container -p 80:80 vsource_control 
```

The user interface should now be visible by typing `0.0.0.0` into the browser of the computer running docker. If docker was installed on a remote host computer on the same network, view the UI by directing the browser to the ip address of the host computer. 
</details>

## Various Useful Docker Commands

<details>
<summary> Docker commands needed for starting/stopping/updating a container</summary>

### Build command:
```console
docker build -t vsource_control .
```

run command:
### to make a new container from updated image:
```console
docker run -d --restart unless-stopped --name vsource_control_container -p 80:80 vsource_control 
```


### to run existing container
```console
docker run -d -p 80:80 vsource_control -d --restart unless-stopped
```


### Stop and remove existing container:
```console
docker rm -f vsource_control_container
```

### remove 'dangling' images. 

If you remove a container and make a new image with the same name as an old one, the old image is not deleted. It loses it's name and becomes a 'dangling image'. Remove these with:

```
docker image prune
```


Note: if you're changing something like CSS, you might need to rebuild the container with no cache. The docker rebuid process is iterative and might not 'notice' that a particular file needs to be updated:
```console
docker build -t vsource_control . --no-cache
```
### to see the console outputs of the container (including outputs from python's `print()`)
1. get the container id:
```console
docker ps
```
2. view the logs in real time
```console
docker logs -f <container_id>
```
</details>


## Development
<details>
<summary>Initial steps for adding functionality to the web-based frontend or the python backend</summary>

### Architecture

Inside the /frontend folder, the web-based user interface is defined. By running a command in this folder, all code to operate this web-based software is compiled into several files which are placed in `/backend/dbay_control/`. The backend may then load and 'serve' this code. If you look inside the `package.json` file in `frontend`, you'll see that `npm run build` has been customized to compile the code with `vite build` and copy it to `/backend/snspd_bias_control/`. So anytime new frontend functionality is added and it's time to get it working with the backend, this command needs to be run. 

### Frontend Development
The frontend code may be previewed and improved without interacting with the python backend. That is, the frontend is 'served' by node (a javascript runtime) instead of the the python backend. The only difference is that the frontend will load a dummy 'fallback state' that doesn't correspond to any state shared with the python backend. 

node and npm need to be installed

```bash
cd frontend
npm install
npm run dev
```

Building the 'look' of a new module in the GUI is fastest by adding it to the fallback state located in `frontend/src/fallbackState.ts`, and watching for changes while the `npm run dev` development server is running. 

#### Running the python server
Using `npm run dev` in the `/frontend` folder does not make use of the python backend at all. The 'backend' is needed to rout commands from the web browser to the hardware, and to be the official source of truth for the 'state' of the device bay system (what modules are plugged in, what voltages and channels are activated or powered, etc.)

If the frontend had been updated in some way, it will have to be recompiled by running `npm run build` in the frontend folder, thereby populating `/backend/snspd_bias_control/` with new html and javascript to serve. 

Use anaconda or pip to install dependencies. For pip:
```bash
pip install --no-cache-dir --upgrade -r requirements.txt
cd backend
python main.py
```

## Development Process
To create the software for a new module, code in both the /frontend and /backend must be added. This is an iterative process that often begins with defining what structs or data packets will be sent and received from what endpoints (e.g. `/dac16D/vsource/`). Here's some steps that don't necessarily need to happen in this order:

1. Create a new ui file `{module_name}.svelte` and core logic file `{module_name}_data.svelte.ts` in `frontend/src/lib/modules_dbay`. The `{module_name}_data.svelte.ts` may make use of the 'addon' classes defined in `frontend/src/lib/addons`. The `frontend/src/modules_day/index.svelte.ts` file must also be updated. Include the imports:

```ts
import { default as {module_name}_component } from './{module_name}.svelte'
import { {module_name} } from './{module_name}_data.svelte'
```

And add the new module/module_component to the `components` and `modules` objects defined below in the same file. 

## Module data structure. 

Module state is defined with a simple hierarchy of dataclasses (python) or objects (javascript/typescript). It's easiest to see the basic structure in `backend/state.py`


2. Create a new python file in `backend/modules/` with name `{module_name}.py`. This python file may import datastructures from `backend/addons`. It must define a `router` using `APIRouter(prefix="/{module_name}", ...)` imported from `fastapi`. This router must also be imported into the `main.py` file (e.g. with `from .modules import {module_name}`), and 'connected' with the rest of the application using `app.include_router({module_name}.router)`. 

NOTE: a library called `pydantic2ts` is used to transform the datastructures found in the addon files like `/backend/addons/vsource.py` to `interface.ts` files found in `frontend/src/lib/addons`. This ensures that the frontend and backend code agree on the 'shape' of data packets sent between them. If files like `/backend/addons/vsource.py` are changed, or new datastructures are defined for get/put requests, then `backend/pydantic_to_typescript.py` should be rerun and possibly updated. Because `pydantic2ts` converts from python to typescript, it makes sense to (1) get your data strucutres defined first in python with pydantic classes, (2) modify `backend/pydantic_to_typescript.py` to create a corresponding `interface.ts` file somewhere inside `frontend/`, and (3) work on the frontend code to use the datastructure from the newly modified/created `interface.ts` file. 

</details>


## Docker Development Notes

<details>
<summary>Commands and notes related to building the docker container</summary>


The uploaded docker image was built on an ARM-based macbook. In order to build an image that will run on an x86-64 platform, you have to use `buildx`, a feature for multi-architecture builds. 




```

# Create a new builder instance
docker buildx create --name mybuilder

# Switch to the new builder instance
docker buildx use mybuilder

# Start up the builder instance
docker buildx inspect --bootstrap

# build the image and pull it to the local docker desktop (?) 
docker buildx build --platform linux/amd64 -t sansseriff/vsource_control . --load
```

Then with the docker desktop utility, publish the image to dockerhub. This way works without signing issues. If I used the --push option for that last command, then the built container had signing issues. I would get this error when trying to pull:

```
Trying to pull repository docker.io/sansseriff/vsource_control ... 
missing signature key
```

</details>
