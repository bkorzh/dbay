from pydantic import BaseModel
from lab_link import ReactiveModel


class ChSenseState(ReactiveModel):
    index: int
    voltage: float
    measuring: bool
    name: str

class IVsenseAddon(ReactiveModel):
    channels: list[ChSenseState]



class VsenseChange(BaseModel):
    module_index: int
    index: int
    voltage: float
    measuring: bool
    name: str