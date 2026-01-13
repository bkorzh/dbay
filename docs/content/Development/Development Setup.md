# Layout

The repository layout:

```folder
  ├── docs
  ├── firmware
  ├── hardware
  ├── software
  |   ├── frontend
  |   ├── backend
  ├── sites
```

- The `docs` directory contains this documentation as an obsidian vault. During a commit to the main branch, the contents of `docs` is copied into corresponding folders in `sites/docs/` and built into a website with quartz.
- The `firmware` folder contains code that is compiled and loaded onto microcontrollers in VME rack itself. 
- The `hardware` folder contains information related to physical construction and design of the VME rack.
- The `software` folder contains `frontend` code to show a graphical user interface in a web-browser or desktop app, and `backend` code written in python for keeping track of the state of the device-bay system. "State" includes which channels are currently turned on, and to what voltage, and which slot contains which module, and so on. 
- The `sites/docs` directory contains the parent quartz website repository as a submodule. This way, the submodule only needs to be downloaded if the website is being built locally. For most development this likely isn't needed, and the work of building the website is handled by github actions. By using a submodule, the latest version of quartz is always used so that explicit updating steps are not required. The `sites/` directory could also contain files related to other websites in the future. 

Follow the below steps to set up a local development environment.
# 1. Clone Repository
The repository is on github.com/bkorzh/dbay/tree/main. We refer to this repository as *dbay-repo* and call the directory it is installed in *path_to_dbay_repo*

# 2. Setup Frontend Development Environment
## Install Bun
### On Linux and MacOS
```bash
curl -fsSL https://bun.sh/install | bash
source ~/.bash_profile 
```
After installation, restart the terminal. 
### On Windows
```powershell
powershell -c "irm bun.sh/install.ps1|iex"
```

After installation, restart the terminal. 

## Install Frontend dependencies

Change the working directory
```bash
cd path_to_dbay_repo/software/frontend
```
Go into the frontend directory, and run `bun install`

```bash
bun install
bun trust --all
```

# 3. Setup  Backend Development Environment 
To contribute to the backend development, please set up your machine following these steps.
## Python environment
The backend currently uses python 3.11.  Create a virtual environment with this python version and install the dependencies in the dbay-repo in *software/backend/pyproject.toml*. This section explains the recommended procedure to install the environment.

### On Linux
Check if your system already runs on python 3.11. If not, install it, e.g. via your distributions package manager. On Ubuntu for example:
```shell
sudo apt install python311
```
Additionally, you might have to install the corresponding pip:
```shell
sudo apt install python3.11-pip
```
Install pipx with
```bash
python3.11 -m pip install --user pipx 
python3.11 -m pipx ensurepath
```
Refer to [the pipx website](https://pipx.pypa.io/stable/installation/) for details.
Install poetry with
```bash
python3.11 -m pipx install poetry
```
Configure poetry to create a local virtual environment (.venv folder)
```bash
poetry config virtualenvs.in-project true
```
Change the directory to path_to_dbay_repo/software/backend*:
```bash
cd path_to_dbay_repo/software/backend
```
Ensure the environment created will use python 3.11:
```bash
poetry env use python3.11
```
In *path_to_dbay_repo/software/backend* , run
```bash
poetry install
```
This should create a `.venv` folder in `software/backend` and install the required dependencies listed in *pyproject.toml*

The entry point of the backend is the *main.py* file in *path_to_dbay_repo/backend/backend*. There, the IP address of the control module has to be entered in the variable 

# 4. Run the build script

Run: 

```bash
cd path_to_dbay_repo/software/frontent
bun ./build.ts --frontend
```
# 5. Start the Application
Run
```bash
cd path_to_dbay_repo/software/backend
eval $(poetry env activate)
python3.11 backend/main.py
```
There should appear a line in the terminal like
```bash
INFO:     Uvicorn running on http://0.0.0.0:8345 (Press CTRL+C to quit)
```
click on the IP address displayed or copy it in a browser to access the GUI.

To connect to a control module, click on the Menu (three horizontal bars in the top-right) and then on *Re-initialize Source* . In the appearing box, enter the IP address of the control module (see [[Setup the Control Module Firmware]] to find the IP).

You will have to add firewall rules on linux to access the web gui on another machine. For Ubuntu this would be
```bash
sudo ufw allow 8345
sudo ufw reload
```
# TODO

- sections about rust/tauri and flatpak not included here from old version in [[Development]]