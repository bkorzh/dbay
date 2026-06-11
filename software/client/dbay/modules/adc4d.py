from __future__ import annotations

from typing import Any, Optional
from dbay.direct import DeviceConnection

__all__ = ["ADC4D"]


class ADC4D:
    CORE_TYPE = "ADC4D"
    """Dual-mode ADC4D module.

    Direct commands:
      - read_diff(channel) -> "ADC4D VRD <slot> <channel>"

    GUI mode not implemented.
    """

    def __init__(
        self,
        data,
        *,
        sync: Any = None,
        connection: Optional[DeviceConnection] = None,
        mode: str = "gui",
        retain_changes: bool = True,
    ):
        self.mode = mode.lower()
        if self.mode not in {"gui", "direct"}:
            raise ValueError("mode must be 'gui' or 'direct'")
        self.sync = sync
        self.connection = connection
        self.data = data
        self.slot = data.get("core", {}).get("slot", 0)
        self.retain_changes = retain_changes

    def read_diff(self, channel: int):
        if not (0 <= channel <= 4):
            raise ValueError("channel must be 0..4")
        if self.mode == "gui":
            assert self.sync is not None
            result = self.sync.send_command(
                "set_adc4d_vsense",
                {
                    "module_index": self.slot,
                    "index": channel,
                    "voltage": 0.0,
                    "measuring": True,
                    "name": self._channel_name(channel),
                },
            )
            self._refresh()
            if isinstance(result, dict) and "voltage" in result:
                return result["voltage"]
            return self._channel_voltage(channel)
        assert self.connection is not None
        return self.connection.send(f"ADC4D VRD {self.slot} {channel}")

    # Alias for semantic clarity
    def read_differential(self, channel: int):
        return self.read_diff(channel)

    def __str__(self):  # pragma: no cover
        return f"ADC4D (Slot {self.slot}) [{'direct' if self.mode=='direct' else 'gui'}]"

    def _refresh(self):
        if self.sync is None:
            return
        self.data = self.sync.module_data(self.slot)

    def _channel(self, channel: int) -> dict[str, Any]:
        channels = self.data.get("vsense", {}).get("channels", [])
        if isinstance(channels, list) and channel < len(channels):
            value = channels[channel]
            if isinstance(value, dict):
                return value
        return {}

    def _channel_name(self, channel: int) -> str:
        return str(self._channel(channel).get("name", f"CH{channel}"))

    def _channel_voltage(self, channel: int) -> float:
        return float(self._channel(channel).get("voltage", 0.0))
