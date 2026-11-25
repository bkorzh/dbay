from pydantic import BaseModel
from lab_link import ReactiveModel



# STATE ##################################
class ChSourceState(ReactiveModel):
    index: int
    bias_voltage: float
    activated: bool
    heading_text: str
    measuring: bool


class IVsourceAddon(ReactiveModel):
    channels: list[ChSourceState]



# MESSAGE ##################################
class VsourceChange(BaseModel):
    module_index: int
    index: int
    bias_voltage: float
    activated: bool
    heading_text: str
    measuring: bool

class SharedVsourceChange(BaseModel):
    change: VsourceChange # the change to apply
    link_enabled: list[bool] # the channels to apply the change to




