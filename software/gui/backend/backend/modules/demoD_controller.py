"""State model and hardware controller for the demoD tutorial module.

demoD is not real hardware. It exists so that
`docs/content/Development/Adding a Module.md` can walk through adding a module
against code that actually runs, and so that a test keeps that walkthrough
honest. It is deliberately small: one voltage channel that reuses the vsource
addon, plus one plain float field driven by a slider.

Unlike the real modules, `DemoDState` is defined here rather than in
`dbay.state`. Real module schemas belong in the client package so the Python
client validates them; keeping a fake module out of the published package is
worth the trade, and it exercises the plugin point — `module_registry` feeds
`build_system_state_model()`, so a backend can add module types the client has
never heard of. Clients without this model see the slot as
`dbay.state.UnknownModuleState` and keep working.

Hardware commands are delegated to the client package's `dac4D` module, so the
demo drives real DAC4D commands rather than inventing a wire protocol: the
voltage channel is hardware channel 0, and the slider's trim voltage is
hardware channel 1.
"""

from typing import Literal

from dbay.modules.dac4d import dac4D as ClientDac4D
from dbay.state import ChSourceState, Core, IVsourceAddon, ModuleState

from backend.dbay_bridge import dbay_client
from backend.server_logging import get_logger
from backend.udp_control import Controller, ParentUDP


logger = get_logger(__name__)

# The slider's range. Narrower than the hardware's, to keep the tutorial's
# validation example concrete.
TRIM_MIN = -1.0
TRIM_MAX = 1.0

# Hardware channels behind the two controls.
OUTPUT_CHANNEL = 0
TRIM_CHANNEL = 1


class DemoDState(ModuleState):
    """One voltage channel plus a trim voltage set by a slider."""

    module_type: Literal["demoD"] = "demoD"
    core: Core
    vsource: IVsourceAddon
    trim_voltage: float = 0.0


def create_prototype(slot: int) -> DemoDState:
    """What a freshly added demoD looks like before anything touches it."""
    channels = [
        ChSourceState(
            index=0,
            bias_voltage=0.0,
            activated=False,
            heading_text="",
            measuring=False,
        )
    ]
    return DemoDState(
        core=Core(slot=slot, type="demoD", name="my demoD module"),
        vsource=IVsourceAddon(channels=channels),
        trim_voltage=0.0,
    )


class demoDController(Controller):
    """Delegates to the client package's dac4D module for UDP commands."""

    def __init__(self, parent_udp: ParentUDP, module_slot: int):
        super().__init__(parent_udp, "DAC4D")
        self.module_slot = module_slot
        self._module = dbay_client.attach_module(module_slot, ClientDac4D)
        logger.info("demoDController initialized for slot %s", self.module_slot)
        self.setDevice(self.module_slot)

    def set_output_voltage(self, voltage: float) -> int:
        """Drive the main output. Returns 0 on success, -1 on failure."""
        return self._send(OUTPUT_CHANNEL, voltage)

    def set_trim_voltage(self, voltage: float) -> int:
        """Drive the trim output — the same command on a different channel."""
        return self._send(TRIM_CHANNEL, voltage)

    def _send(self, channel: int, voltage: float) -> int:
        try:
            self._module.set_voltage(channel, voltage)
        except Exception as exc:
            logger.error("demoD set_voltage failed: %s", exc)
            return -1
        logger.debug(
            "demoD slot=%s channel=%s voltage=%s", self.module_slot, channel, voltage
        )
        return 0
