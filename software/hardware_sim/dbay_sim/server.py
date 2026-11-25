"""Virtual DBay hardware: a UDP server that mimics the Teensy firmware.

Implements the ASCII command protocol from ``dbayfirmware/dbay_ctrlFW.ino``:

    SETDEV <board> <type>                 -> "+ok"
    DAC4D  VS|VSD <board> <ch> <voltage>  -> "+ok"
    DAC16D VS|VSD <board> <ch> <voltage>  -> "+ok"
    DAC16D VSB <board> <voltage>          -> "+ok"
    DAC16D VR <board>                     -> ",<float>"
    DAC4ETH VS|VSD <board> <ch> <voltage> -> "+ok"
    ADC4D  VRD <board> <ch>               -> ",<float>"
    reset                                 -> "+ok"
    debug on|off                          -> "+ok"
    help                                  -> "-<help text>"

Response framing matches the firmware's ``format_message``:
    error  -> "-<message>\\n"
    int    -> ":<int>\\n"
    float  -> ",<float .6f>\\n"
    ok     -> "+ok\\n"

ADC readings are randomized: each ADC channel performs a slow random walk
around a per-channel base value with gaussian noise, so the GUI shows
plausibly drifting live voltages.
"""

from __future__ import annotations

import logging
import random
import socket
import threading

logger = logging.getLogger("dbay_sim")

MAX_MODULES = 8

DEVICE_TYPES = {"DAC4D", "DAC16D", "ADC4D", "DAC4ETH", "FAFD", "HIC4", "NODEV"}

HELP_TEXT = (
    "Available commands:\n"
    "SETDEV [board] [device]\n"
    "DAC4D [VS/VSD] [board] [channel] [voltage]\n"
    "DAC4ETH [VS/VSD] [board] [channel] [voltage]\n"
    "DAC16D [VS/VSD] [board] [channel] [voltage]\n"
    "DAC16D VSB [board] [voltage]\n"
    "DAC16D VR\n"
    "debug [on/off]\n"
    "reset\n"
    "help"
)


def _parse_int(token: str) -> int | None:
    try:
        return int(token, 10)
    except ValueError:
        return None


def _parse_float(token: str) -> float | None:
    try:
        return float(token)
    except ValueError:
        return None


class AdcChannel:
    """A randomized voltage source: slow random walk + gaussian read noise."""

    def __init__(self, rng: random.Random, walk: float = 0.002, noise: float = 0.0005):
        self._rng = rng
        self._walk = walk
        self._noise = noise
        self._value = rng.uniform(-0.2, 0.2)

    def read(self) -> float:
        self._value += self._rng.gauss(0.0, self._walk)
        self._value = max(-5.0, min(5.0, self._value))
        return self._value + self._rng.gauss(0.0, self._noise)


class VirtualModule:
    def __init__(self, device_type: str, rng: random.Random):
        self.device_type = device_type
        # DAC outputs: channel -> last set voltage (kept for inspection/debug)
        self.voltages: dict[int, float] = {}
        # ADC4D has 5 differential read channels in the firmware (VRD 0..4);
        # DAC16D has one differential read-back channel (VR).
        self.adc_channels: dict[int, AdcChannel] = {}
        if device_type == "ADC4D":
            self.adc_channels = {ch: AdcChannel(rng) for ch in range(5)}
        elif device_type == "DAC16D":
            self.adc_channels = {0: AdcChannel(rng)}


class VirtualDBay:
    """Pure protocol engine: feed it command lines, get firmware-style replies."""

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)
        self.modules: list[VirtualModule | None] = [None] * MAX_MODULES
        self.debug = False

    # ── firmware-equivalent helpers ──────────────────────────────────────

    def _check_module(self, board: int, expected: str) -> str | None:
        """Returns an error string, or None when the board matches."""
        module = self.modules[board]
        if module is None:
            return f"board is not initialized, use SETDEV"
        if module.device_type != expected:
            return "use SETDEV with the proper board type"
        return None

    def _setdev(self, tokens: list[str]) -> str:
        if len(tokens) != 3:
            return self._error("SETDEV requires 2 arguments: [address] [device type]")
        board = _parse_int(tokens[1])
        if board is None or board < 0 or board > 7:
            return self._error(f"Invalid board number: {tokens[1]}")
        devtype = tokens[2]
        if devtype not in DEVICE_TYPES:
            return self._error("wrong devtype")
        if devtype == "NODEV":
            return self._ok()
        module = self.modules[board]
        if module is None or module.device_type != devtype:
            self.modules[board] = VirtualModule(devtype, self._rng)
            logger.info("SETDEV: board %d is now %s", board, devtype)
        return self._ok()

    # ── response framing (firmware format_message) ───────────────────────

    @staticmethod
    def _error(message: str) -> str:
        return f"-{message}\n"

    @staticmethod
    def _ok() -> str:
        return "+ok\n"

    @staticmethod
    def _float(value: float) -> str:
        return f",{value:.6f}\n"

    # ── command dispatch ─────────────────────────────────────────────────

    def handle(self, line: str) -> str:
        tokens = line.split()
        if not tokens:
            return self._error("Empty command received.")

        command = tokens[0]

        if command == "SETDEV":
            return self._setdev(tokens)

        if command in DEVICE_TYPES and command != "NODEV":
            return self._device_command(command, tokens)

        if command == "debug":
            if len(tokens) != 2:
                return self._error("debug command expects 1 argument: debug [on/off]")
            arg = tokens[1].lower()
            if arg in {"on", "1"}:
                self.debug = True
            elif arg in {"off", "0"}:
                self.debug = False
            else:
                return self._error(f"Invalid argument for debug: {tokens[1]}")
            return self._ok()

        if command == "reset":
            self.modules = [None] * MAX_MODULES
            logger.info("reset: all modules cleared")
            return self._ok()

        if command == "help":
            return self._error(HELP_TEXT)

        return self._error(f"Unknown command: {command}")

    def _device_command(self, devtype: str, tokens: list[str]) -> str:
        if len(tokens) < 3:
            return self._error(f"{devtype} requires a function and board number")
        func = tokens[1]
        board = _parse_int(tokens[2])
        if board is None or board < 0 or board > 7:
            return self._error(f"Invalid board number: {tokens[2]}")
        check = self._check_module(board, devtype)
        if check is not None:
            return self._error(check)
        module = self.modules[board]
        assert module is not None

        if devtype == "DAC4D":
            if func == "VS":
                return self._set_voltage(module, tokens, ch_min=0, ch_max=7)
            if func == "VSD":
                return self._set_voltage(module, tokens, ch_min=0, ch_max=3)
            return self._error("unknown command for DAC4D")

        if devtype in {"DAC16D", "DAC4ETH"}:
            if func == "VS":
                return self._set_voltage(module, tokens, ch_min=0, ch_max=31)
            if func == "VSD":
                return self._set_voltage(module, tokens, ch_min=-3, ch_max=15)
            if devtype == "DAC16D" and func == "VR":
                return self._float(module.adc_channels[0].read())
            if devtype == "DAC16D" and func == "VSB":
                if len(tokens) != 4:
                    return self._error("DAC16D VSB requires 4 arguments, type help")
                voltage = _parse_float(tokens[3])
                if voltage is None:
                    return self._error(f"Invalid voltage value: {tokens[3]}")
                module.voltages[-1] = voltage
                return self._ok()
            return self._error(f"unknown command for {devtype}")

        if devtype == "ADC4D":
            if func == "VRD":
                if len(tokens) != 4:
                    return self._error("ADC4D VRD requires 4 arguments, type help")
                channel = _parse_int(tokens[3])
                if channel is None or channel < 0 or channel > 4:
                    return self._error(f"Invalid channel number: {tokens[3]}")
                return self._float(module.adc_channels[channel].read())
            return self._error("unknown command for ADC4D")

        # FAFD / HIC4: firmware accepts and does nothing
        return self._ok()

    @staticmethod
    def _set_voltage(module: VirtualModule, tokens: list[str], *, ch_min: int, ch_max: int) -> str:
        if len(tokens) != 5:
            return VirtualDBay._error(f"{tokens[0]} {tokens[1]} requires 5 arguments, type help")
        channel = _parse_int(tokens[3])
        if channel is None or channel < ch_min or channel > ch_max:
            return VirtualDBay._error(f"Invalid channel number: {tokens[3]}")
        voltage = _parse_float(tokens[4])
        if voltage is None:
            return VirtualDBay._error(f"Invalid voltage value: {tokens[4]}")
        module.voltages[channel] = voltage
        logger.info("%s: board ch%d <- %+.4f V", tokens[0], channel, voltage)
        return VirtualDBay._ok()


class SimServer:
    """UDP transport wrapper around VirtualDBay."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8880, seed: int | None = None):
        self.host = host
        self.port = port
        self.device = VirtualDBay(seed=seed)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host, port))
        self.port = self._socket.getsockname()[1]
        self._socket.settimeout(0.5)
        self._running = False
        self._thread: threading.Thread | None = None

    def serve_forever(self) -> None:
        self._running = True
        logger.info("DBay hardware simulator listening on %s:%d", self.host, self.port)
        while self._running:
            try:
                data, addr = self._socket.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            message = data.decode(errors="replace").strip()
            response = self.device.handle(message)
            logger.debug("%s -> %r => %r", addr, message, response)
            try:
                self._socket.sendto(response.encode(), addr)
            except OSError:
                break

    def start(self) -> "SimServer":
        """Run the server in a background thread (for tests / embedding)."""
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._socket.close()

    def __enter__(self) -> "SimServer":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()
