from pydantic import BaseModel
from backend.addons.vsource import IVsourceAddon
from backend.addons.vsense import IVsenseAddon

from backend.addons.vsource import ChSourceState
# from backend.addons.vsense import ChSenseState

class Core(BaseModel):
    slot: int
    type: str
    name: str

class IModule(BaseModel):
    core: Core
    vsource: IVsourceAddon | None = None
    vsense: IVsenseAddon | None = None

class SystemState(BaseModel):
    data: list[IModule]
    valid: bool
    dev_mode: bool

class VMEParams(BaseModel):
    ipaddr: str
    timeout: int
    port: int
    dev_mode: bool

ch1 = ChSourceState(index=0, bias_voltage=0, activated=True, heading_text="1st ch dac4D", measuring=False)
ch2 = ChSourceState(index=1, bias_voltage=0, activated=True, heading_text="2nd ch dac4D", measuring=False)
ch3 = ChSourceState(index=2, bias_voltage=0, activated=False, heading_text="3rd ch dac4D", measuring=False)
ch4 = ChSourceState(index=3, bias_voltage=0, activated=False, heading_text="4th ch dac4D", measuring=False)

data = [IModule(core=Core(slot=i, type="empty", name="empty")) for i in range(8)]

data[3] = IModule(core=Core(slot=3, type="dac4D", name="my dac4D"), vsource=IVsourceAddon(channels=[ch1, ch2, ch3, ch4]))

# create default state
# module_1 = IModule(core=Core(slot=3, type="dac4D", name="my dac4D"), vsource=IVsourceAddon(channels=[ch1, ch2, ch3, ch4]))
system_state = SystemState(data=data, valid=True, dev_mode=False)