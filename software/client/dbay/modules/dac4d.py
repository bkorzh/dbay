from dbay.http import Http
from dbay.addons.vsource import VsourceChange
from dbay.state import IModule, Core
from typing import Literal, Union, Optional
from dbay.addons.vsource import IVsourceAddon
from dbay.direct import DeviceConnection

MODE_GUI = 'gui'
MODE_DIRECT = 'direct'


class dac4D_spec(IModule):
    module_type: Literal["dac4D"] = "dac4D"
    core: Core
    vsource: Optional[IVsourceAddon] = None  # optional in direct mode


class dac4D_direct:
    """
    Use this class if the GUI is not needed.
    """

    def __init__(self, connection, slot: int):
        self._slot: int = slot
        self._connection = connection

    def set_voltage(self, channel: int, voltage: float,
                    activated: Union[bool, None] = None):
        """Set voltage on a channel using VSD (differential) command.

        This is the standard voltage-setting method for dac4D.
        """
        if not (0 <= channel <= 3):
            raise ValueError("channel must be 0..3")
        if not (-10 <= voltage <= 10):
            raise ValueError("voltage must be -10..10 V")

        assert self._connection is not None
        self._connection.send(f"DAC4D VSD {self._slot} {channel} {voltage}")

    def set_voltage_single(self, channel: int, voltage: float, *args, **kwargs):
        """Set single-ended voltage output using VS command.

        Use set_voltage() for standard differential output.
        """
        if not (0 <= channel <= 7):
            raise ValueError("channel must be 0..7")
        if not (-10 <= voltage <= 10):
            raise ValueError("voltage must be -10..10 V")

        assert self._connection is not None
        self._connection.send(f"DAC4D VS {self._slot} {channel} {voltage}")

    # Backwards compatibility alias
    def voltage_set(self, channel: int, voltage: float,
                    activated: Union[bool, None] = None):
        """Legacy alias for set_voltage()."""
        return self.set_voltage(channel, voltage, activated=activated)

    # Backwards compatibility alias
    def set_voltage_diff(self, channel: int, voltage: float):
        """Alias for set_voltage() - VSD is now the default."""
        return self.set_voltage(channel, voltage)

    def __str__(self):
        return f"dac4D (Slot {self._slot}) [direct]"


class dac4D_http:
    CORE_TYPE = "dac4D"
    """Dual-mode dac4D module wrapper.

    GUI mode expects full `data` including vsource. Direct mode can pass a
    minimal core structure: {"core": {"slot": int, "type": "dac4D", "name": str}}.
    """

    def __init__(
            self,
            data,
            *,
            http: Optional[Http] = None,
            retain_changes: bool = True,
    ):

        self.http = http
        self.retain_changes = retain_changes
        self.data = dac4D_spec(**data)

    # ------------------------------------------------------------------
    # GUI-only cleanup (revert config). Direct mode does nothing.
    # ------------------------------------------------------------------
    def __del__(self):  # pragma: no cover - defensive cleanup
        if self.retain_changes:
            return
        if not self.data.vsource or not self.http:
            return
        try:
            for idx in range(min(4, len(self.data.vsource.channels))):
                ch = self.data.vsource.channels[idx]
                change = VsourceChange(
                    module_index=self.data.core.slot,
                    index=idx,
                    bias_voltage=ch.bias_voltage,
                    activated=ch.activated,
                    heading_text=ch.heading_text,
                    measuring=False,
                )
                self.http.put("dac4D/vsource/", data=change.model_dump())
        except Exception:
            # Avoid destructor exceptions
            pass

    # ------------------------------------------------------------------
    # Unified API
    # ------------------------------------------------------------------
    def set_voltage(self, channel: int, voltage: float,
                    activated: Union[bool, None] = None):
        """Set voltage on a channel using VSD (differential) command.

        This is the standard voltage-setting method for dac4D.
        """
        if not (0 <= channel <= 3):
            raise ValueError("channel must be 0..3")
        if not (-10 <= voltage <= 10):
            raise ValueError("voltage must be -10..10 V")
        if activated is None:
            activated = self.data.vsource.channels[
                channel].activated  # type: ignore
        change = VsourceChange(
            module_index=self.data.core.slot,
            index=channel,
            bias_voltage=voltage,
            activated=activated,
            heading_text=self.data.vsource.channels[
                channel].heading_text,  # type: ignore
            measuring=True,
        )
        assert self.http is not None
        self.http.put("dac4D/vsource/", data=change.model_dump())

    def set_voltage_single(self, channel: int, voltage: float):
        """Set single-ended voltage output using VS command.

        Use set_voltage() for standard differential output.
        """

        raise NotImplementedError(
            "Single-ended voltage not exposed in GUI")

    # Backwards compatibility aliases
    def voltage_set(self, channel: int, voltage: float,
                    activated: Union[bool, None] = None):
        """Legacy alias for set_voltage()."""
        return self.set_voltage(channel, voltage, activated=activated)

    def set_voltage_diff(self, channel: int, voltage: float):
        """Alias for set_voltage() - VSD is now the default."""
        return self.set_voltage(channel, voltage)

    def __str__(self):
        slot = self.data.core.slot
        if self.data.vsource:
            active_channels = sum(
                1 for ch in self.data.vsource.channels if ch.activated)
            return f"dac4D (Slot {slot}): {active_channels}/4 channels active"
        return f"dac4D (Slot {slot}) [direct]"


class dac4D:
    CORE_TYPE = "dac4D"
    """Dual-mode dac4D module wrapper.

    GUI mode expects full `data` including vsource. Direct mode can pass a
    minimal core structure: {"core": {"slot": int, "type": "dac4D", "name": str}}.
    """

    def __init__(
            self,
            data,
            *,
            http: Optional[Http] = None,
            connection: Optional[DeviceConnection] = None,
            mode: str = MODE_GUI,
            retain_changes: bool = True,
    ):

        self.mode = mode.lower()
        if self.mode not in {MODE_GUI, MODE_DIRECT}:
            raise ValueError(f"mode must be '{MODE_GUI}' or '{MODE_DIRECT}'")
        self.http = http
        self.retain_changes = retain_changes
        # In direct mode vsource may be absent; allow None
        self.data = dac4D_spec(**data)


        # TODO: in principle, this initialization could be done outside
        # this class and dac4D_http or dac4D_direct could be given as an
        # argument to this class.
        if self.mode == MODE_GUI:
            self._dac4D = dac4D_http(data,
                                     http=http,
                                     retain_changes=retain_changes)
        elif self.mode == MODE_DIRECT:
            self._dac4D = dac4D_direct(connection=connection,
                                       slot=self.data.core.slot)

    # ------------------------------------------------------------------
    # Unified API
    # ------------------------------------------------------------------
    def set_voltage(self, channel: int, voltage: float,
                    activated: Union[bool, None] = None):
        """Set voltage on a channel using VSD (differential) command.
        
        This is the standard voltage-setting method for dac4D.
        """

        self._dac4D.set_voltage(channel, voltage, activated=activated)

    def set_voltage_single(self, channel: int, voltage: float):
        """Set single-ended voltage output using VS command.
        
        Use set_voltage() for standard differential output.
        """
        self._dac4D.set_voltage_single(channel, voltage)

    # Backwards compatibility aliases
    def voltage_set(self, channel: int, voltage: float,
                    activated: Union[bool, None] = None):
        """Legacy alias for set_voltage()."""
        return self.set_voltage(channel, voltage, activated=activated)

    def set_voltage_diff(self, channel: int, voltage: float):
        """Alias for set_voltage() - VSD is now the default."""
        return self.set_voltage(channel, voltage)

    def __str__(self):
        return self._dac4D.__str__()
