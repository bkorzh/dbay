Working on the firmware, software, or documentation for the device bay system starts with cloning the repository. 

```shell
git clone https://github.com/bkorzh/dbay.git
```

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
- The `software` folder contains `frontend` code to show a graphical user interface in a web-browser (and possibly in the future for a stand-alone desktop app), and `backend` code written in python for keeping track of the state of the device-bay system. "State" includes which channels are currently turned on, and to what voltage, and which slot contains which module, and so on. 
- The `sites/docs` directory contains the parent quartz website repository as a submodule. This way, the submodule only needs to be downloaded if the website is being built locally. For most development this likely isn't needed, and the work of building the website handled by github actions. By using a submodule, the latest version of quartz is always used so that explicit updating steps are not required. The `sites/` directory could also contain files related to other websites in the future. 



# Development Setup

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