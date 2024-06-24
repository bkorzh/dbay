from backend.addons.vsource import VsourceChange, ChSourceState
from backend.server_logging import get_logger
from backend.location import BASE_DIR
import csv
from datetime import datetime

import os

logger = get_logger(__name__)

def identify_change(change: VsourceChange, old_channel_state: ChSourceState):
    change_dict = change.model_dump()
    old_channel_state_dict = old_channel_state.model_dump()
    module = change_dict["module_index"]
    index = change_dict["index"]
    del change_dict["module_index"]
    diff = {
        key: (value, old_channel_state_dict.get(key))
        for key, value in change_dict.items()
        if old_channel_state_dict.get(key) != value
    }
    diff.update(
        {
            key: (None, value)
            for key, value in old_channel_state_dict.items()
            if key not in change_dict
        }
    )
    board = change.module_index

    change_strings = [
        f"Module index {module} (slot {board}), channel {index}: {key} changed from {old_value} to {new_value}"
        for key, (new_value, old_value) in diff.items()
    ]
    logger.info(f"Changes: {change_strings}")
    return diff


def write_state_to_csv(change: VsourceChange, changed_str: str):
    with open(os.path.join(BASE_DIR, "log.csv"), "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                datetime.now(),
                changed_str,
                change.index,
                change.bias_voltage,
                change.activated,
                change.heading_text,
                change.module_index,
            ]
        )