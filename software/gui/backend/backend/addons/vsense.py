from pydantic import BaseModel


class ChSenseState(BaseModel):
    index: int
    voltage: float
    measuring: bool
    name: str

class IVsenseAddon(BaseModel):
    channels: list[ChSenseState]



class VsenseChange(BaseModel):
    module_index: int
    index: int
    voltage: float
    measuring: bool
    name: str