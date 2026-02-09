from backend.module import IModule, Core
from backend.addons.vsource import IVsourceAddon, ChSourceState
from backend.addons.vsense import ChSenseState
from typing import Literal
from backend.server_logging import get_logger
from backend.udp_control import Controller, ParentUDP
from backend.dbay_bridge import dbay_client
from dbay.modules.dac16d import dac16D as ClientDac16D

logger = get_logger(__name__)



class dac16D(IModule):
    """Backend state model for dac16D module (tracks GUI state)."""
    module_type: Literal["dac16D"] = "dac16D"
    core: Core
    vsource: IVsourceAddon
    vsb: ChSourceState
    vr: ChSenseState


def create_prototype(slot: int):
    channels = [ChSourceState(index=i, bias_voltage=0, activated=False, heading_text=f"{i}th ch dac16D", measuring=False) for i in range(16)]
    vsb = ChSourceState(index=0, bias_voltage=0, activated=False, heading_text="dac16D vsb", measuring=False)
    vr = ChSenseState(index=0, voltage=0, measuring=False, name="dac16D vr")
    return dac16D(core=Core(slot=slot, type="dac16D", name="my dac16D module"), vsource=IVsourceAddon(channels=channels), vsb=vsb, vr=vr)




class dac16DController(Controller):
    """Controller that delegates UDP commands to device-bay-client module."""
    
    def __init__(self, parent_udp: ParentUDP, module_slot: int):
        super().__init__(parent_udp, "DAC16D")
        self.module_slot = module_slot

        # Attach a client module for this slot
        self._module = dbay_client.attach_module(module_slot, ClientDac16D)

        logger.info(f"dac16DController initialized for slot {self.module_slot}")
        self.setDevice(self.module_slot)

    def setChVol(self, board: int, channel: int, voltage: float):
        """Set channel voltage using device-bay-client module."""
        if board < 0 or board > 7:
            logger.error("error, board out of range")
            return -1
        if voltage < -20 or voltage > 20:
            logger.error("error, voltage out of range")
            return -1
        
        try:
            # Delegate to client module - set_voltage now sends VSD
            self._module.set_voltage(channel, voltage)
            logger.debug(f"dac16D setChVol: slot={board}, channel={channel}, voltage={voltage}")
            return 0
        except Exception as e:
            logger.error(f"dac16D setChVol failed: {e}")
            return -1

    def setBias(self, voltage: float):
        """Set bias voltage using device-bay-client module."""
        try:
            self._module.set_bias(voltage)
            logger.debug(f"dac16D setBias: voltage={voltage}")
            return 0
        except Exception as e:
            logger.error(f"dac16D setBias failed: {e}")
            return -1

    def readV(self, board: int):
        """Read voltage using device-bay-client module."""
        if board < 0 or board > 7:
            return "error, board out of range"
        try:
            return self._module.read()
        except Exception as e:
            logger.error(f"dac16D readV failed: {e}")
            return f"error: {e}"