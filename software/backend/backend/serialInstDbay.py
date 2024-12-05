"""
serialInstDBAY.py
Author: Andrew Mueller, based on code by Alex Walter, with inspiration from
        the old JPL Library of snspd-scripts written by Simone Frasca, Boris Korzh
Date: Dec 3, 2024

A generic base class to talk to DABY hardware over serial port
"""
import serial
import time


class serialInstDbay():
    """
    Generic base class for an instrument connected over serial port
    """

    def __init__(self, port: str, timeout: int=5, offline: bool=False, baudrate: int=9600):
        """

        :param port: The serial port
        :param timeout: the serial timeout
        :param offline: For testing purposes when your computer is not connected to the instrument
        """
        self.serial = serial.Serial()
        self.timeout = timeout
        self.port = port
        self.serial.port = port
        self.serial.timeout = timeout
        self.serial.baudrate = baudrate
        self.offline = offline

    def connect(self):
        #print('serial connect')
        if self.offline:
            print("Connected to offline instrument "+str(self.__class__))
            return True
        return self.serial.open()

    def disconnect(self):
        # print('serial disconnect')
        if self.offline:
            print("Disconnected from offline instrument " + str(self.__class__))
            return True
        return self.serial.close()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    

    def read_until_none_left(self):
        """
        Seems to avoid most issues with the serial connection getting into weird states
        """
        lines: list[str] = []

        while True:
            if self.offline:
                return ''
            if self.serial.in_waiting:
                line = self.serial.readline()
                lines.append(line.decode())
            else:
                break

        return ''.join(lines)

    def read(self):
        lines: list[str] = []
        lines.extend(self.read_until_none_left())
        time.sleep(0.001)
        lines.extend(self.read_until_none_left())
        return ''.join(lines)


    def write(self, cmd: bytes):
        #print('serial write')
        if self.offline: return True
        self.serial.flush()
        return self.serial.write(cmd)

    def query(self, cmd: bytes):
        #print('serial query')
        self.write(cmd)
        return self.read()
    

    def query_newline(self, cmd: str):
        command = (cmd + "\n").encode()
        return self.query(command)