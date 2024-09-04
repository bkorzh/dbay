
from backend.location import DATA_DIR
import json
import os

from backend.state import Core, SystemState, Empty
from backend.addons.vsource import IVsourceAddon
from backend.addons.vsource import ChSourceState
# from backend.modules.dac4D_spec import dac4D
from typing import Any, Type

from backend.udp_control import Controller, parent_udp

import importlib
import importlib.util

from typing import Literal, Union, Type, Any, Callable
from typing import cast
from pydantic import BaseModel

from backend.modules.dac4D_spec import dac4DController
# import sys

from backend.modules import dac4D_spec
from backend.modules import dac16D_spec


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__)) # needed for pyinstaller to work


# # create a default testing state
# data: list[Any]  = [Empty(core=Core(slot=i, type="empty", name="empty")) for i in range(8)]

# channels = [ChSourceState(index=i, bias_voltage=0, activated=False, heading_text=f"{i}th ch dac4D", measuring=False) for i in range(4)]
# data[3] = dac4D(core=Core(slot=3, type="dac4D", name="empty"), vsource=IVsourceAddon(channels=channels))

# channels_2 = [ChSourceState(index=i, bias_voltage=0, activated=False, heading_text=f"{i}th ch dac4DM2", measuring=False) for i in range(4)]
# data[6] = dac4D(core=Core(slot=6, type="dac4D", name="empty"), vsource=IVsourceAddon(channels=channels_2))


# # load dev mode setting. If true, python does not acctually send UDP messages to the rack. 
# with open(os.path.join(BASE_DIR, "vsource_params.json"), "r") as f:
#     vsource_params= json.load(f)
# system_state = SystemState(data=data, valid=True, dev_mode=vsource_params["dev_mode"])





class GlobalState:
    def __init__(self):

        data: list[Any]  = [Empty(core=Core(slot=i, type="empty", name="empty")) for i in range(8)]

        # print("base dir", BASE_DIR)
        # print("base dir files", os.listdir(BASE_DIR))
        with open(os.path.join(DATA_DIR, "vsource_params.json"), "r") as f:
            vsource_params= json.load(f)


        self.system_state = SystemState(data=data, valid=True, dev_mode=vsource_params["dev_mode"])
        self.controllers: list[Controller] = [Controller(parent_udp, "empty") for _ in range(8)]

    # @staticmethod
    # def load_modules_from_directory(directory: str) -> dict[str, Type[Any]]:
    #     modules: dict[str, Any] = {}
    #     for filename in os.listdir(directory):
    #         # print(filename)
    #         if filename.endswith('_spec.py') and filename != '__init__.py':
    #             module_name = filename[:-8]  # remove '_spec.py' from filename
    #             module = importlib.import_module(f'.{module_name}_spec', package=f"backend.{directory}")
    #             modules[module_name] = module
    #     return modules
    

    # @staticmethod
    # def load_modules_from_directory(directory: str) -> dict[str, Type[Any]]:
    #     modules: dict[str, Any] = {}

    #     directory = os.path.join(SCRIPT_PATH, directory)

    #     for filename in os.listdir(directory):
    #         if filename.endswith('_spec.py') and filename != '__init__.py':
    #             module_name = filename[:-8]  # remove '_spec.py' from filename
    #             module_path = os.path.join(directory, filename)
    #             spec = importlib.util.spec_from_file_location(module_name, module_path)
    #             if spec and spec.loader:
    #                 module = importlib.util.module_from_spec(spec)
    #                 spec.loader.exec_module(module)
    #                 modules[module_name] = module
    #     return modules



    def add_module(self, module_type: str, slot: int):

        # modules = self.load_modules_from_directory('modules')

        # this is not dynamic, but it's a start.
        modules = {"dac4D": dac4D_spec, "dac16D": dac16D_spec}
        # get the create_prototype() function from a module file, like dac4D_spec.create_prototype()

        # print("module_type", module_type)
        creator = cast(Callable[[int], BaseModel], modules[module_type].create_prototype)
        controller_class = cast(Type[dac4DController], getattr(modules[module_type], f'{module_type}Controller'))

        model = creator(slot)
        controller_instance = controller_class(parent_udp, slot)

        self.system_state.data[slot] = model # type: ignore
        self.controllers[slot] = controller_instance



global_state = GlobalState()