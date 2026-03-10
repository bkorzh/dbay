from dataclasses import dataclass
from typing import Callable

from backend.module import IModule
from backend.modules.adc4D_spec import adc4D, adc4DController, create_prototype as create_adc4D
from backend.modules.dac16D_spec import dac16D, dac16DController, create_prototype as create_dac16D
from backend.modules.dac4D_spec import dac4D, dac4DController, create_prototype as create_dac4D
from backend.udp_control import Controller, ParentUDP


@dataclass(frozen=True)
class ModuleRegistration:
    model_class: type[IModule]
    create_prototype: Callable[[int], IModule]
    controller_class: Callable[[ParentUDP, int], Controller]


# Add new backend modules here. Each module should be imported above and added to
# this dictionary so the backend state and initialization logic stay in sync.
REGISTERED_MODULES: dict[str, ModuleRegistration] = {
    "dac4D": ModuleRegistration(
        model_class=dac4D,
        create_prototype=create_dac4D,
        controller_class=dac4DController,
    ),
    "dac16D": ModuleRegistration(
        model_class=dac16D,
        create_prototype=create_dac16D,
        controller_class=dac16DController,
    ),
    "adc4D": ModuleRegistration(
        model_class=adc4D,
        create_prototype=create_adc4D,
        controller_class=adc4DController,
    ),
}

REGISTERED_MODULE_MODELS: tuple[type[IModule], ...] = tuple(
    registration.model_class for registration in REGISTERED_MODULES.values()
)
