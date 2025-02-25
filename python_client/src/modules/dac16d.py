class dac16D:
    def __init__(self, data):
        self.data = data

    async def voltage_set_shared(self, change):
        # Implement the logic to call the /vsource_shared/ endpoint
        pass

    async def voltage_set(self, change):
        # Implement the logic to call the /vsb/ endpoint
        pass

    async def websocket_vsense(self):
        # Implement the logic to call the /ws_vsense/ endpoint
        pass

    async def read_voltage(self, board):
        # Implement the logic to read voltage from the specified board
        pass

    # Add any additional methods as needed based on the requirements of the application