import json
import os
from typing import Any

from backend.location import DATA_DIR
from backend.module import Core
from backend.module_registry import REGISTERED_MODULES
from backend.state import Empty, SystemState
from backend.udp_control import Controller, parent_udp


class GlobalState:
    """
    This class is a singleton representing the global state.
    """
    _instance: "GlobalState | None" = None

    data: list[Any]
    system_state: SystemState
    controllers: list[Controller]

    def __new__(cls, vsource_params: str | None = None):
        """
        This method is called when GlobalState() is executed but before __init__. It allows to check if there is
        already an instance of the global state and return it if so. Else, a new global state is created.

        :param vsource_params: configuration file for Voltage Source
        """
        if cls._instance is not None:
            return cls._instance

        cls._instance = super(GlobalState, cls).__new__(cls)
        instance = cls._instance

        instance.data = [Empty(core=Core(slot=i, type="empty", name="empty")) for i in range(8)]

        # for backwards compatibility:
        vsource_params_path = vsource_params or os.path.join(DATA_DIR, "vsource_params.json")

        with open(vsource_params_path, "r") as f:
            vsource_config: dict[str, Any] = json.load(f)

        instance.system_state = SystemState(data=instance.data, valid=True, dev_mode=vsource_config["dev_mode"])
        instance.controllers = [Controller(parent_udp, "empty") for _ in range(8)]

        return instance

    def add_module(self, module_type: str, slot: int):
        try:
            registration = REGISTERED_MODULES[module_type]
        except KeyError as exc:
            raise ValueError(f"Unknown module type: {module_type}") from exc

        model = registration.create_prototype(slot)
        controller_instance = registration.controller_class(parent_udp, slot)

        self.system_state.data[slot] = model  # type: ignore
        self.controllers[slot] = controller_instance

    def __str__(self):
        return f"{self.__class__.__name__}(system_state={self.system_state})"


# TODO this call should be made in the files where global_state is used
global_state = GlobalState()
