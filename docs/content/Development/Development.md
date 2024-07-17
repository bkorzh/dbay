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