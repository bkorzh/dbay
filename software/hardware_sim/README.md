# DBay hardware simulator

A stdlib-only UDP server that mimics the DBay Teensy firmware
(`dbayfirmware/dbay_ctrlFW/dbay_ctrlFW.ino`), for developing and testing the
GUI backend and the `dbay` client without a physical rack.

It speaks the same ASCII protocol on UDP port **8880**:

| Command                                | Reply           |
| -------------------------------------- | --------------- |
| `SETDEV <board> <type>`                | `+ok`           |
| `DAC4D VS\|VSD <board> <ch> <v>`       | `+ok`           |
| `DAC16D VS\|VSD <board> <ch> <v>`      | `+ok`           |
| `DAC16D VSB <board> <v>`               | `+ok`           |
| `DAC16D VR <board>`                    | `,<float>`      |
| `DAC4ETH VS\|VSD <board> <ch> <v>`     | `+ok`           |
| `ADC4D VRD <board> <ch>`               | `,<float>`      |
| `reset`                                | `+ok`           |
| `debug on\|off`                        | `+ok`           |
| `help`                                 | `-<help text>`  |
| anything else / bad arguments          | `-<error>`      |

Like the firmware, device commands fail with `-board is not initialized, use
SETDEV` until the board has been assigned a type, and with `-use SETDEV with
the proper board type` on a type mismatch.

ADC4D readings (`VRD`) and the DAC16D read-back (`VR`) return randomized
voltages: each channel does a slow random walk around a per-channel base value
with a little gaussian read noise, so the GUI shows live, drifting values.

## Running

```bash
cd software/hardware_sim
uv run dbay-sim                 # listens on 0.0.0.0:8880
uv run dbay-sim -v --seed 42    # log every exchange, reproducible readings
```

or without uv:

```bash
python -m dbay_sim --port 8880
```

## Pointing the GUI backend at the simulator

Either edit the backend's `config/vsource_params.json`:

```json
{"ipaddr": "127.0.0.1", "port": 8880, "dev_mode": false}
```

or, with the GUI running, open the connection settings ("Re-init source") and
set address `127.0.0.1`, port `8880`, with dev mode **off** (dev mode stubs
out UDP entirely).

## Using from the dbay client (direct mode)

```python
from dbay.client import DBayClient
from dbay.modules.adc4d import ADC4D

client = DBayClient(mode="direct", direct_host="127.0.0.1", direct_port=8880)
adc = client.attach_module(2, ADC4D)
print(adc.read_diff(0))   # ",0.093214" — firmware-style float reply
```
