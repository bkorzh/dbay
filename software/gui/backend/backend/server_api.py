import socket

import psutil
from lab_link import CommandContext, CommandError, ptr
from pydantic import BaseModel

from backend.initialize import global_state
from backend.server_logging import get_logger
from backend.sync import sync
from backend.udp_control import UDP, parent_udp


logger = get_logger(__name__)
SERVE_PORT = 8345


class ModuleAddition(BaseModel):
    slot: int
    type: str


class VsourceParams(BaseModel):
    ipaddr: str
    timeout: float
    port: int
    dev_mode: bool


def _command_error(code: str, message: str, *, path: str | None = None) -> CommandError:
    return CommandError(
        code=code,
        message=message,
        display="toast",
        severity="warning",
        path=path,
        recoverable=True,
    )


@sync.command
def initialize_module(ctx: CommandContext, **params):
    addition_args = ModuleAddition(**params)

    if addition_args.slot < 0 or addition_args.slot >= len(global_state.system_state.data):
        raise _command_error(
            "invalid_slot",
            f"Slot {addition_args.slot + 1} is outside the rack range.",
            path=ptr("data", addition_args.slot),
        )

    try:
        # the slot assignment inside add_module broadcasts the change
        global_state.add_module(addition_args.type, addition_args.slot)
    except ValueError as exc:
        raise _command_error(
            "invalid_module_type",
            str(exc),
            path=ptr("data", addition_args.slot),
        ) from exc

    return global_state.system_state.model_dump(mode="json")


@sync.command
def initialize_vsource(ctx: CommandContext, **params):
    vsource_params = VsourceParams(**params)
    global_state.system_state.dev_mode = vsource_params.dev_mode
    parent_udp.udp = UDP(vsource_params.ipaddr, vsource_params.port, vsource_params.dev_mode)

    logger.info(
        "udp control re-initialized with params: %s",
        vsource_params.model_dump(),
    )
    return vsource_params.model_dump(mode="json")


@sync.command
def get_server_info(ctx: CommandContext, **params):
    # Collect every non-loopback IPv4 address; with multiple network cards the
    # server is reachable on several of them.
    ipaddrs: list[str] = []
    for addrs in psutil.net_if_addrs().values():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                if addr.address not in ipaddrs:
                    ipaddrs.append(addr.address)

    if not ipaddrs:
        ipaddrs = ["127.0.0.1"]

    return {"ipaddr": ipaddrs[0], "ipaddrs": ipaddrs, "port": SERVE_PORT}
