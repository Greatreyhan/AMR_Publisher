import string
import serial
import time

class Com_Model:
    port : string
    ser : serial

    def __init__(self,port):
        self.port = port
        self.ser = serial.Serial(port,
                                 baudrate=115200,
                                 timeout=5.0,
                                 bytesize=8,
                                 parity='N',
                                 stopbits=1)
        
    def checksum_pc_generator(self, data):
        checksum = sum(data) & 0xFF
        return checksum
    
    def parse_packet(self, data):
        if len(data) != 16:
            return False, None

        # Verify the start bytes
        if data[:2] != bytes([0xA5, 0x5A]):
            return False, None

        # Verify the checksum
        checksum = self.checksum_pc_generator(data[:-1])
        if checksum != data[-1]:
            return False, None

        return True, data[2:-1]

    def startCom(self):
        while True:
            datas = self.ser.read(16)
            valid, parsed_data = self.parse_packet(datas)
            if valid:
                print("Parsed Data:", parsed_data)
            else:
                print("Invalid Packet")