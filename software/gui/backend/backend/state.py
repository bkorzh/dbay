from pydantic import BaseModel, Field

from typing import Literal, Union
from typing_extensions import Annotated

from backend.module import IModule, Core
from backend.module_registry import REGISTERED_MODULE_MODELS


class Empty(IModule):
    module_type: Literal["empty"] = "empty"
    core: Core


GenericModule = Annotated[
    Union[Empty, *REGISTERED_MODULE_MODELS],
    Field(discriminator='module_type'),
]  # type: ignore

'''
NOTE: SystemState.data can NOT just be a list of IModule. Though IModule is a base class for all the modules,
it has a smaller set of fields than real modules. Pydantic would validate away the extra fields in the real modules.
You need the tagged Union[Empty, ...registered module models...] to be able to validate the real modules.

'''

class SystemState(BaseModel):
    data: list[GenericModule]
    valid: bool
    dev_mode: bool
    

class VMEParams(BaseModel):
    ipaddr: str
    timeout: int
    port: int
    dev_mode: bool





