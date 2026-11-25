"""System state model, built from the shared schema plus this backend's registry.

The module *schema* lives in :mod:`dbay.state` so the Python client validates
against the same definition. Which modules are valid, however, is a backend
concern — `module_registry` is a plugin point — so the concrete SystemState is
built here from the registered models. Module types absent from the registry
still validate, as `dbay.state.UnknownModuleState`.
"""

from pydantic import BaseModel

from dbay.state import EmptyState as Empty
from dbay.state import build_system_state_model

from backend.module_registry import REGISTERED_MODULE_MODELS


SystemState = build_system_state_model(*REGISTERED_MODULE_MODELS)


class VMEParams(BaseModel):
    ipaddr: str
    timeout: int
    port: int
    dev_mode: bool


__all__ = ["Empty", "SystemState", "VMEParams"]
