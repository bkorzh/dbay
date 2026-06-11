from __future__ import annotations

from typing import Any

from fastapi import APIRouter, WebSocket
from lab_link import LabSync, ptr

from backend.initialize import global_state
from backend.state import SystemState


sync = LabSync()
sync.register_state(SystemState, initial=global_state.system_state)

router = APIRouter()


@router.websocket("/sync/ws")
async def sync_websocket(websocket: WebSocket) -> None:
    await sync._handle_ws(websocket)  # type: ignore[attr-defined]


def replace_sync_state() -> None:
    sync.replace_state(global_state.system_state)


def set_sync_value(path: str, value: Any) -> None:
    sync.set(path, value)


def publish_vsource_channel(module_index: int, channel_index: int) -> None:
    module = global_state.system_state.data[module_index]
    channel = module.vsource.channels[channel_index]  # type: ignore[attr-defined]

    with sync.transaction() as tx:
        tx.set(
            ptr("data", module_index, "vsource", "channels", channel_index, "bias_voltage"),
            channel.bias_voltage,
        )
        tx.set(
            ptr("data", module_index, "vsource", "channels", channel_index, "activated"),
            channel.activated,
        )
        tx.set(
            ptr("data", module_index, "vsource", "channels", channel_index, "heading_text"),
            channel.heading_text,
        )
        tx.set(
            ptr("data", module_index, "vsource", "channels", channel_index, "measuring"),
            channel.measuring,
        )


def publish_vsource_channels(module_index: int, channel_indices: list[int]) -> None:
    module = global_state.system_state.data[module_index]

    with sync.transaction() as tx:
        for channel_index in channel_indices:
            channel = module.vsource.channels[channel_index]  # type: ignore[attr-defined]
            tx.set(
                ptr("data", module_index, "vsource", "channels", channel_index, "bias_voltage"),
                channel.bias_voltage,
            )
            tx.set(
                ptr("data", module_index, "vsource", "channels", channel_index, "activated"),
                channel.activated,
            )
            tx.set(
                ptr("data", module_index, "vsource", "channels", channel_index, "heading_text"),
                channel.heading_text,
            )
            tx.set(
                ptr("data", module_index, "vsource", "channels", channel_index, "measuring"),
                channel.measuring,
            )


def publish_vsense_channel(module_index: int, channel_index: int) -> None:
    module = global_state.system_state.data[module_index]
    channel = module.vsense.channels[channel_index]  # type: ignore[attr-defined]

    with sync.transaction() as tx:
        tx.set(
            ptr("data", module_index, "vsense", "channels", channel_index, "voltage"),
            channel.voltage,
        )
        tx.set(
            ptr("data", module_index, "vsense", "channels", channel_index, "measuring"),
            channel.measuring,
        )
        tx.set(
            ptr("data", module_index, "vsense", "channels", channel_index, "name"),
            channel.name,
        )


def publish_vsense_voltages(module_index: int, channel_indices: list[int]) -> None:
    """Publish only the voltage values of the given channels in one transaction."""
    module = global_state.system_state.data[module_index]

    with sync.transaction() as tx:
        for channel_index in channel_indices:
            channel = module.vsense.channels[channel_index]  # type: ignore[attr-defined]
            tx.set(
                ptr("data", module_index, "vsense", "channels", channel_index, "voltage"),
                channel.voltage,
            )


def publish_adc4d_polling(module_index: int) -> None:
    module = global_state.system_state.data[module_index]
    polling = module.polling  # type: ignore[attr-defined]

    with sync.transaction() as tx:
        tx.set(ptr("data", module_index, "polling", "running"), polling.running)
        tx.set(ptr("data", module_index, "polling", "frequency"), polling.frequency)


def publish_dac16d_vsb(module_index: int) -> None:
    module = global_state.system_state.data[module_index]
    channel = module.vsb  # type: ignore[attr-defined]

    with sync.transaction() as tx:
        tx.set(ptr("data", module_index, "vsb", "bias_voltage"), channel.bias_voltage)
        tx.set(ptr("data", module_index, "vsb", "activated"), channel.activated)
        tx.set(ptr("data", module_index, "vsb", "heading_text"), channel.heading_text)
        tx.set(ptr("data", module_index, "vsb", "measuring"), channel.measuring)
