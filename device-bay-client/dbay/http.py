import requests


class Http:
    def __init__(self, server_address: str, port: int):
        self.server_address = server_address
        self.port = port

    def get(self, endpoint: str):
        response = requests.get(f"http://{self.server_address}:{self.port}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get data from {endpoint}")

    def put(self, endpoint: str, data: dict):
        response = requests.put(
            f"http://{self.server_address}:{self.port}/{endpoint}", json=data
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to put data to {endpoint}")
