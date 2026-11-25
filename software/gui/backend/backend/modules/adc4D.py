import asyncio

from pydantic import BaseModel

from backend.addons.vsense import VsenseChange
from backend.initialize import global_state
from typing import cast
from backend.server_logging import get_logger
from backend.modules.adc4D_spec import (
    MAX_POLLING_HZ,
    MIN_POLLING_HZ,
    NUM_CHANNELS,
    adc4D,
    adc4DController,
)
from backend.sync import sync
from lab_link import CommandContext, CommandError, ptr


logger = get_logger(__name__)

# slot -> running polling task
_polling_tasks: dict[int, asyncio.Task] = {}


class PollingChange(BaseModel):
    module_index: int
    running: bool
    frequency: float


def _command_error(
    code: str,
    message: str,
    *,
    path: str | None = None,
    display: str = "toast",
    severity: str = "warning",
) -> CommandError:
    return CommandError(
        code=code,
        message=message,
        display=display,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        path=path,
        recoverable=True,
    )


def _get_adc4d(module_index: int) -> adc4D:
    try:
        module = global_state.system_state.data[module_index]
    except IndexError as exc:
        raise _command_error(
            "invalid_module",
            f"Slot {module_index + 1} is not an adc4D module.",
            path=ptr("data", module_index),
        ) from exc

    if module.core.type != "adc4D":
        raise _command_error(
            "invalid_module",
            f"Slot {module_index + 1} is not an adc4D module.",
            path=ptr("data", module_index),
        )

    return cast(adc4D, module)


@sync.command
async def set_adc4d_vsense(ctx: CommandContext, **params):
    change = VsenseChange(**params)
    module = _get_adc4d(change.module_index)

    if change.index < 0 or change.index >= NUM_CHANNELS:
        raise _command_error(
            "invalid_channel_index",
            f"Channel {change.index} is outside the adc4D range.",
            path=ptr("data", change.module_index, "vsense"),
        )

    controller = cast(adc4DController, global_state.controllers[change.module_index])

    # One-shot read on enabling measurement so the display updates immediately,
    # without waiting for the next polling tick.
    if change.measuring:
        voltage = await asyncio.to_thread(
            controller.readChannelVoltage, change.module_index, change.index
        )
    else:
        voltage = 0.0

    sense_channel = module.vsense.channels[change.index]
    sense_channel.name = change.name
    sense_channel.measuring = change.measuring
    sense_channel.voltage = voltage
    change.voltage = voltage

    return change.model_dump(mode="json")


@sync.command
async def set_adc4d_polling(ctx: CommandContext, **params):
    change = PollingChange(**params)
    module = _get_adc4d(change.module_index)

    frequency = min(max(change.frequency, MIN_POLLING_HZ), MAX_POLLING_HZ)

    module.polling.running = change.running
    module.polling.frequency = frequency

    task = _polling_tasks.get(change.module_index)
    if change.running:
        if task is None or task.done():
            _polling_tasks[change.module_index] = asyncio.create_task(
                _poll_adc4d(change.module_index)
            )
    elif task is not None:
        task.cancel()
        _polling_tasks.pop(change.module_index, None)

    return {
        "module_index": change.module_index,
        "running": change.running,
        "frequency": frequency,
    }


async def _poll_adc4d(module_index: int) -> None:
    """Poll the hardware for all measuring channels until polling is stopped.

    Frequency changes take effect on the next tick because the live module
    state is re-read every iteration. The loop also exits on its own if the
    slot is re-initialized as a different module type.
    """
    logger.info(f"adc4D polling started for slot {module_index}")
    try:
        while True:
            module = global_state.system_state.data[module_index]
            if module.core.type != "adc4D" or not module.polling.running:  # type: ignore[attr-defined]
                break
            module = cast(adc4D, module)
            controller = cast(adc4DController, global_state.controllers[module_index])

            measuring = [ch.index for ch in module.vsense.channels if ch.measuring]
            if measuring:
                voltages = await asyncio.to_thread(
                    lambda: [controller.readChannelVoltage(module_index, i) for i in measuring]
                )
                # same-tick writes batch into one patch; if the slot was
                # re-initialized, the orphaned module swallows them harmlessly
                for index, voltage in zip(measuring, voltages):
                    module.vsense.channels[index].voltage = voltage

            await asyncio.sleep(1.0 / module.polling.frequency)
    except asyncio.CancelledError:
        pass
    finally:
        logger.info(f"adc4D polling stopped for slot {module_index}")
