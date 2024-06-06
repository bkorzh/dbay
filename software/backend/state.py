from pydantic import BaseModel
from backend.addons.vsource import IVsourceAddon
from backend.addons.vsense import IVsenseAddon

from backend.addons.vsource import ChSourceState
# from backend.addons.vsense import ChSenseState

from backend.location import BASE_DIR
import os
import json



class Core(BaseModel):
    slot: int
    type: str
    name: str

class IModule(BaseModel):
    core: Core

class SystemState(BaseModel):
    data: list[IModule]
    valid: bool
    dev_mode: bool
    

class VMEParams(BaseModel):
    ipaddr: str
    timeout: int
    port: int
    dev_mode: bool


