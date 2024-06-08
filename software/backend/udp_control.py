import socket
import select
# Sender function
import os
import json
from backend.location import BASE_DIR

class UDP:
    def __init__(self, ip: str, port: int, dev_mode: bool, timeout: int = 1):    
        self._ip = ip
        self._port = port
        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._timeout = timeout
        self.dev_mode = dev_mode

    def __del__(self):
        self._udp_socket.close()

    def send_message(self, message: str) -> str:
        if not self.dev_mode:
            try:
                # Send the message to the target IP and port
                self._udp_socket.sendto(message.encode(), (self._ip, self._port))
                # Initialize a counter for failed attempts
                failed_attempts = 0
                while True:
                    # Wait for a response with a short timeout
                    ready = select.select([self._udp_socket], [], [], 1)
                    if ready[0]:
                        # Receive the response from the server
                        data, _ = self._udp_socket.recvfrom(self._port)
                        response = data.decode()
                        return response
                    else:
                        # Increment the counter for failed attempts
                        failed_attempts += 1
                        # If the counter reaches a threshold, return an error message
                        if failed_attempts >= 10:  # adjust this value as needed
                            return "Error: No response from the server"
                    # Check if a KeyboardInterrupt has been raised
                    if KeyboardInterrupt:
                        break
                return "Error: break"
            
            except Exception as e:
                return "Error: {}".format(str(e))
        else:
            return '+ok\n'
        

# an object that contains the udp class that's never overwritten. This way, the udp object can be refreshed
# while keeping access to it available for all modules. 
class ParentUDP:
    def __init__(self, udp: UDP):
        self.udp = udp


# load defuault ip address and port
with open(os.path.join(BASE_DIR, "vsource_params.json"), "r") as f:
    vsource_params = json.load(f)
    udp_control = UDP(vsource_params["ipaddr"], vsource_params["port"], dev_mode = vsource_params["dev_mode"])
    parent_udp = ParentUDP(udp_control)


# modules inherit this to create a class for managing setup of the module when first plugged in. 
class Controller:
    def __init__(self, parent_udp: ParentUDP, module_type: str):
        self.parent_udp = parent_udp
        self.module_type = module_type

    def setDevice(self, board: int) -> str:
        message = ""

        print("this is board")
        if board < 0 or board > 7:
            return "error, board out of range"
        else:
            message = "SETDEV" + str(board) + str(self.module_type) + "\n"
        return self.parent_udp.udp.send_message(message)