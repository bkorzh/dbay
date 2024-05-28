from pydantic import BaseModel



# STATE ##################################
class ChSourceState(BaseModel):
    index: int
    bias_voltage: float
    activated: bool
    heading_text: str
    measuring: bool


class IVsourceAddon(BaseModel):
    channels: list[ChSourceState]



# MESSAGE ##################################
class VsourceChange(BaseModel):
    module_index: int
    index: int
    bias_voltage: float
    activated: bool
    heading_text: str
    measuring: bool




