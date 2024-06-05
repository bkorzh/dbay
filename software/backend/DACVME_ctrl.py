import socket
import select
# Sender function



class VMECTRL:


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
        
        

    def setDACVol(self, board: int, dacchan: int, voltage: float) -> str:
        message = ""
        if board <0 or board > 7:
            return "error, board out of range"
        if dacchan <0 or dacchan > 15:
            return "error, channel out of range"
        if  voltage < -10  or voltage > 10:
            return "error, voltage out of range"
        else:
            message = "SetDAC "+ str(board) + " " + str(dacchan) + " " + str(voltage) + "\n"
        
        return self.send_message(message)

    def setChVol(self, board: int, diffchan: int, voltage: float):
        if board <0 or board > 7:
            print("error, board out of range")
            return -1
        if diffchan <0 or diffchan > 7:
            print("error, channel out of range")
            return -1
        if  voltage < -20  or voltage > 20:
            return "error, voltage out of range"
        else:
            r1 = self.setDACVol(board, diffchan*2, voltage/2)
            r2 = self.setDACVol(board, diffchan*2+1, -voltage/2)
            # r1 = self.setDACVol(board, diffchan, voltage)
            # r2 = '+ok\n'
            print(r1)
            print(r2)
            if r1 == '+ok\n' and r2 == '+ok\n':
                return 0
            else: 
                return -1