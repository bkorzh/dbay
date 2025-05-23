# dbay-client/README.md

# DBay Client

DBay is a Python client for interacting with the DBay web server. This client allows you to manage and control various modules such as `dac4D` and `dac16D` through a simple interface.

## Installation

You can install the DBay client directly from PyPI:

```bash
pip install dbay
```

Alternatively, you can clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd dbay-client
pip install -e .
```

## Usage

To use the DBay client, you need to create an instance of the `DBay` class with the server address (IP address and port). The client will automatically call the `/full-state` endpoint to retrieve the current state of the server.

```python
from dbay.client import DBay
import time

# Initialize the client with the server address
# Use ip address of the computer running the DBay gui program.
# make sure port 8345 is open on this computer's firewall
client = DBay("<ip address>")  # Default port is used. 

# List all modules and their current status
client.list_modules()
# Example output:
# DBay Modules:
# -------------
# Slot 0: dac4D (Slot 0): 2/4 channels active
# Slot 1: dac16D (Slot 1): 0/16 channels active
# Slot 2: Empty slot
# Slot 3: Empty slot
# Slot 4: Empty slot
# Slot 5: Empty slot
# Slot 6: Empty slot
# Slot 7: Empty slot
# -------------

# Working with a dac4D module in slot 1
client.modules[0].voltage_set(0, 1)  # Set channel 0 to 1V
client.modules[0].voltage_set(0, 2, activated=True)  # Set and activate channel 0
client.modules[0].voltage_set(0, 3.33)  # Set channel 0 to 3.33V

# Working with a dac16D module in slot 2
client.modules[1].voltage_set(0, 1, activated=True)  # Set and activate channel 0
client.modules[1].voltage_set(1, 2, activated=True)  # Set and activate channel 1

# Setting multiple channels at once
channels = [True, False] * 8  # Select alternating channels
client.modules[1].voltage_set_shared(1.5, channels=channels)  # Set selected channels to 1.5V
```

## Modules

The client supports the following modules:

- **dac4D**: Represents a DAC4D module and includes methods for controlling its functionality.
- **dac16D**: Represents a DAC16D module and includes methods for controlling its functionality.
- **Empty**: Represents an empty module.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.