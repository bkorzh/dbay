from backend.module import IModule, Core
from backend.addons.vsource import IVsourceAddon, ChSourceState
from typing import Literal
from backend.udp_control import Controller, ParentUDP
from backend.dbay_bridge import dbay_client
from dbay.modules.dac4d import dac4D as ClientDac4D

from backend.server_logging import get_logger
logger = get_logger(__name__)



class dac4D(IModule):
    """Backend state model for dac4D module (tracks GUI state)."""
    module_type: Literal["dac4D"] = "dac4D"
    core: Core
    vsource: IVsourceAddon


def create_prototype(slot: int):
    channels = [ChSourceState(index=i, bias_voltage=0, activated=False, heading_text="", measuring=False) for i in range(4)]
    return dac4D(core=Core(slot=slot, type="dac4D", name="my dac4D module"), vsource=IVsourceAddon(channels=channels))



class dac4DController(Controller):
    """Controller that delegates UDP commands to device-bay-client module."""
    
    def __init__(self, parent_udp: ParentUDP, module_slot: int):
        super().__init__(parent_udp, "DAC4D")
        self.module_slot = module_slot

        # Attach a client module for this slot
        self._module = dbay_client.attach_module(module_slot, ClientDac4D)

        logger.info(f"dac4DController initialized for slot {self.module_slot}")
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
            logger.debug(f"dac4D setChVol: slot={board}, channel={channel}, voltage={voltage}")
            return 0
        except Exception as e:
            logger.error(f"dac4D setChVol failed: {e}")
            return -1