from backend.state import IModule, Core
from backend.addons.vsource import IVsourceAddon, ChSourceState




class dac4D(IModule):
    core: Core
    vsource: IVsourceAddon



def create_prototype(slot: int) -> IModule:
    channels = [ChSourceState(index=i, bias_voltage=0, activated=True, heading_text=f"{i}th ch dac4D", measuring=False) for i in range(4) ]
    dac4D_prototype = dac4D(core=Core(slot=slot, type="dac4D", name="my dac4D"), vsource=IVsourceAddon(channels=channels))
    return dac4D_prototype
