
## Layout

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



## Development Setup

### For customizing or extending either the graphical user interface or the python server

### 1. Install Bun

Bun is a newer alternative to nodejs. It is a javascript runtime used to install and manage the frontend framework svelte. 

For details, see the [Bun installation guide](https://healthy.kaiserpermanente.org/failover/failover.htm)

**Linux and macOS**

```bash
curl -fsSL https://bun.sh/install | bash
```

**Windows**
```powershell
powershell -c "irm bun.sh/install.ps1|iex"
```

After installation, restart the terminal. 

### 2. Clone repo

```shell
git clone https://github.com/bkorzh/dbay.git
```

Go into the frontend directory, and run `bun install`

```bash
cd /software/frontend
bun install
```

All the dependencies to view and modify the 'front end' (html/javascript/css) of the app should be installed. You can see it inside a browser buy running `bun run dev`in the terminal, and selecting the **Local** link that shows up, usually something like `http:/localhost:XXXX/`. Or, past this string in your browser. Shut down this development server with CTRL-C. 

## 3. Install rust and other tauri dependencies
Refer to [this guide](https://v2.tauri.app/start/prerequisites/)

### 3. Install Poetry and setup backend

Install python 3.11. This can be a stand-alone python installation or an anaconda environment. You can [install a miniconda package for this](https://docs.anaconda.com/miniconda/miniconda-other-installer-links/): 

1. Install pipx. Use `python3` or just `python`. Whichever works. 
```bash
python3 -m pip install --user pipx 
python3 -m pipx ensurepath
```

Refer to [the pipx website](https://pipx.pypa.io/stable/installation/) for details.

2. Install poetry
```bash
pipx install poetry
```
Refer to [the poetry website](https://python-poetry.org/docs/#installing-with-pipx) for details. Again on windows, I had to restart vscode for the `pipx` command to work. 

Configure poetry to create a local virtual environment (.venv folder), and set it to use python 3.11

```bash
poetry config virtualenvs.in-project true
```

Ensure the environment created will us python 3.11:
```bash
poetry env use python3.11
```

In `software/backend`, run `poetry install`. This should create a `.env` folder in `software/backend`. 

## 4. Run the build script

Go back to `software/frontend` and run: 

```bash
bun ./build.ts --frontend




## X. Install and use flatpack

```
sudo apt install flatpak flatpak-builder
```


ran this from the "Building your first Flatpack" page. Not sure it's necessary.

flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo


Need these:

```
flatpak install flathub org.gnome.Sdk//46
flatpak install flathub org.gnome.Platform//46
```


Command to build:

fllatpak-builder --force-clean --user --repo=repo --install builddir device-bay-flatpack.yml


command to run:
flatpak run com.device.bay



command to build bundle:

flatpak build-bundle repo device-bay.flatpak com.device.bay --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo




You will have to add firewall rules on linux to access the web gui on another machine

```bash
sudo ufw allow 8345
sudo ufw reload
```



## UV


uv python install 3.13

uv venv



uv pip install -r pyproject.toml

### VSCode Python Support

If you're using VScode and the python plugin, it's nice to have language server support for type checking of libraries and [intellisense](https://code.visualstudio.com/docs/editor/intellisense). For this to work, VScode needs to know the path to your python interpreter. 

Run `uv run which python` in the terminal to get the path to the local interpreter in `.venv`. Then in vscode, type `Command` + `Shift` + `p`, then start typing 'select interpreter', and select the `Python: Select Interpreter` option. Click `Enter Interpreter Path`, copy/past the path in, and press enter. With that, all the imports in your python files should change to cyan, and you should be able to naviate through the imports by `Command`-clicking on them. 