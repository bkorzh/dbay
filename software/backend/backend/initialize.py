import importlib
import json
import os
from typing import Type, Any, Callable
from typing import cast

from pydantic import BaseModel

from backend.location import DATA_DIR
from backend.location import MODULE_DIR
from backend.module import Core
from backend.modules.dac4D_spec import dac4DController
from backend.state import SystemState, Empty
from backend.udp_control import Controller, parent_udp


def load_modules_from_directory(directory: str) -> dict[str, Type[Any]]:
    modules: dict[str, Any] = {}

    for filename in os.listdir(directory):
        if filename.endswith('_spec.py') and filename != '__init__.py':
            module_name = filename[:-8]  # remove '_spec.py' from filename
            module_path = os.path.join(directory, filename)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                modules[module_name] = module
    return modules


class GlobalState:
    """
    This class is a singleton representing the global state.
    """
    _instance = None

    def __new__(cls, vsource_params: str | None = None):
        """
        This method is called when GlobalState() is executed but before __init__. It allows to check if there is
        already an instance of the global state and return it if so. Else, a new global state is created.

        :param vsource_params: configuration file for Voltage Source
        """
        if cls._instance is not None:
            return cls._instance

        cls._instance = super(GlobalState, cls).__new__(cls)

        cls._instance.data: list[Any] = [Empty(core=Core(slot=i, type="empty", name="empty")) for i in range(8)]

        # for backwards compatibility:
        if vsource_params is None:
            vsource_params = os.path.join(DATA_DIR, "vsource_params.json")

        with open(vsource_params, "r") as f:
            vsource_params = json.load(f)

        cls._instance.system_state = SystemState(data=cls._instance.data, valid=True,
                                                 dev_mode=vsource_params["dev_mode"])
        cls._instance.controllers: list[Controller] = [Controller(parent_udp, "empty") for _ in range(8)]

        return cls._instance

    def add_module(self, module_type: str, slot: int):
        modules = load_modules_from_directory(MODULE_DIR)

        # this is not dynamic, but it's a start.
        # modules = {"dac4D": dac4D_spec, "dac16D": dac16D_spec, "adc4D": adc4D_spec}
        # get the create_prototype() function from a module file, like dac4D_spec.create_prototype()

        # print("module_type", module_type)
        creator = cast(Callable[[int], BaseModel], modules[module_type].create_prototype)
        controller_class = cast(Type[dac4DController], getattr(modules[module_type], f'{module_type}Controller'))

        model = creator(slot)
        controller_instance = controller_class(parent_udp, slot)

        self.system_state.data[slot] = model  # type: ignore
        self.controllers[slot] = controller_instance

    def __str__(self):
        return f"{self.__class__.__name__}(system_state={self.system_state.data})"


# TODO this call should be made in the files where global_state is used
global_state = GlobalState()
