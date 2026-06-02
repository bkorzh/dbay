from backend.addons.vsource import VsourceChange, SharedVsourceChange
from backend.addons.vsense import ChSenseState
from fastapi import Request, WebSocket
from fastapi import APIRouter, HTTPException
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.dac16D_spec import dac16D, dac16DController
from backend.initialize import global_state
from backend.sync import publish_vsource_channel, publish_vsource_channels, sync
from backend.util import identify_change
from lab_link import CommandContext, CommandError, ptr
import asyncio 
import random


logger = get_logger(__name__)

router = APIRouter(
    prefix="/dac16D",
    responses={404: {"description": "Not found"}},
)


def _command_error(
    code: str,
    message: str,
    *,
    path: str | None = None,
    detail: str | None = None,
    display: str = "toast",
    severity: str = "warning",
) -> CommandError:
    return CommandError(
        code=code,
        message=message,
        detail=detail,
        display=display,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        path=path,
        recoverable=True,
    )


def _validated_change(params: dict) -> tuple[dac16D, VsourceChange]:
    change = VsourceChange(**params)

    try:
        module = cast(dac16D, global_state.system_state.data[change.module_index])
    except IndexError as exc:
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not a dac16D module.",
            path=ptr("data", change.module_index),
        ) from exc

    if module.core.type != "dac16D":
        raise _command_error(
            "invalid_module",
            f"Slot {change.module_index + 1} is not a dac16D module.",
            path=ptr("data", change.module_index),
        )

    if change.index < 0 or change.index > 15:
        raise _command_error(
            "invalid_channel_index",
            f"Channel {change.index} is outside the dac16D range.",
            path=ptr("data", change.module_index, "vsource"),
        )

    change.bias_voltage = round(change.bias_voltage, 4)
    if change.bias_voltage < -5 or change.bias_voltage > 5:
        raise _command_error(
            "voltage_out_of_range",
            f"{change.bias_voltage} V is outside the allowed range.",
            path=ptr(
                "data",
                change.module_index,
                "vsource",
                "channels",
                change.index,
                "bias_voltage",
            ),
        )

    return module, change


def _hardware_error(change: VsourceChange, detail: str) -> CommandError:
    return _command_error(
        "hardware_command_failed",
        "The dac16D voltage source command failed.",
        detail=detail,
        display="banner",
        severity="error",
        path=ptr("data", change.module_index, "vsource", "channels", change.index),
    )


@sync.command
def set_dac16d_vsource(ctx: CommandContext, **params):
    module, change = _validated_change(params)
    controller = cast(dac16DController, global_state.controllers[change.module_index])

    hardware_voltage = change.bias_voltage if change.activated else 0
    result = controller.setChVol(change.module_index, change.index, hardware_voltage)
    if result != 0:
        raise _hardware_error(change, f"setChVol returned {result}")

    source_channel = module.vsource.channels[change.index]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring
    source_channel.activated = change.activated
    source_channel.bias_voltage = change.bias_voltage
    publish_vsource_channel(change.module_index, change.index)

    return change.model_dump(mode="json")


@sync.command
def set_dac16d_vsource_shared(ctx: CommandContext, **params):
    shared_change = SharedVsourceChange(**params)
    module, change = _validated_change(shared_change.change.model_dump())
    controller = cast(dac16DController, global_state.controllers[change.module_index])

    changed_channels: list[int] = []
    for channel_index, linked in enumerate(shared_change.link_enabled[: len(module.vsource.channels)]):
        if not linked:
            continue

        hardware_voltage = change.bias_voltage if change.activated else 0
        result = controller.setChVol(change.module_index, channel_index, hardware_voltage)
        if result != 0:
            failed_change = change.model_copy(update={"index": channel_index})
            raise _hardware_error(failed_change, f"setChVol returned {result}")
        changed_channels.append(channel_index)

    for channel_index in changed_channels:
        source_channel = module.vsource.channels[channel_index]
        source_channel.heading_text = change.heading_text
        source_channel.measuring = change.measuring
        source_channel.activated = change.activated
        source_channel.bias_voltage = change.bias_voltage

    shared_change.change = change
    publish_vsource_channels(change.module_index, changed_channels)

    return shared_change.model_dump(mode="json")


@router.put("/vsource_shared/")
async def voltage_set_shared(request: Request, shared_change: SharedVsourceChange):
    try:
        assert global_state.system_state.data[shared_change.change.module_index].core.type == "dac16D" # type: ignore
    except AssertionError:
        logger.error("Module not dac16D")
        raise HTTPException(status_code=404, detail="Module not dac16D")
    
    slot = shared_change.change.module_index
    assert slot == global_state.system_state.data[shared_change.change.module_index].core.slot # type: ignore
    dac_16d = cast(dac16D, global_state.system_state.data[shared_change.change.module_index]) # type: ignore


    dac16d_controller = cast(dac16DController, global_state.controllers[slot])
    changed_channels: list[int] = []
    for i, boolean in enumerate(shared_change.link_enabled):
        source_channel = dac_16d.vsource.channels[i]

        if boolean:
            source_channel.heading_text = shared_change.change.heading_text
            source_channel.measuring = shared_change.change.measuring
            source_channel.bias_voltage = shared_change.change.bias_voltage
            source_channel.activated = shared_change.change.activated
            if source_channel.activated:
                dac16d_controller.setChVol(slot, i, shared_change.change.bias_voltage)
            else:
                dac16d_controller.setChVol(slot, i, 0)
            changed_channels.append(i)

    publish_vsource_channels(slot, changed_channels)
    return shared_change

@router.put("/vsb/")
async def voltage_set_vsb(request: Request, change: VsourceChange):
    pass


@router.websocket("/ws_vsense/")
async def websocket_vsense_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        number = random.randint(0, 100)/100
        logger.info(f"Received data: {number}")
        vsense_state = ChSenseState(index=0, voltage=number, measuring=True, name="dac16D vr")
        await websocket.send_text(vsense_state.model_dump_json())
        await asyncio.sleep(0.1)

@router.put("/vsource/")
async def voltage_set(request: Request, change: VsourceChange):
    try:
        assert global_state.system_state.data[change.module_index].core.type == "dac16D" # type: ignore
    except AssertionError:
        logger.error("Module not dac16D")
        raise HTTPException(status_code=404, detail="Module not dac16D")
    slot = change.module_index
    assert slot == global_state.system_state.data[change.module_index].core.slot # type: ignore
    dac_16d = cast(dac16D, global_state.system_state.data[change.module_index]) # type: ignore
    change.bias_voltage = round(change.bias_voltage, 4)
    identify_change(
        change, dac_16d.vsource.channels[change.index]
    )
    source_channel = dac_16d.vsource.channels[change.index]
    source_channel.heading_text = change.heading_text
    source_channel.measuring = change.measuring
    dac16d_controller = cast(dac16DController, global_state.controllers[slot])
    source_channel.activated = change.activated
    source_channel.bias_voltage = change.bias_voltage


    try:
        assert (change.index >= 0 and change.index <= 15)
    except AssertionError:
        logger.error("Channel index not in 0-3 range")
        raise HTTPException(status_code=404, detail="Channel index not in 0-3 range")
    

    logger.info(f"change.index: {change.index}")
    if change.activated:
        logger.info(f"turning on {change.index} or already on")
        dac16d_controller.setChVol(slot, change.index, change.bias_voltage)
    else:  # turning on or already on
        logger.info(f"turning off {change.index} or already off")
        dac16d_controller.setChVol(slot, change.index, 0)
        logger.info(f"dac_4d.vsource.channels[change.index]: {dac_16d.vsource.channels[change.index]}")

    publish_vsource_channel(change.module_index, change.index)
    return change
