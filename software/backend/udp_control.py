import socket
import select
# Sender function



class UdpControl:

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