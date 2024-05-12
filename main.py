import serial
import data_parser
import mqtt_publisher

# Define the serial port and baudrate
serial_port = '/dev/ttyUSB0'  # or 'COM1' for Windows
baud_rate = 115200

# Create a serial object
ser = serial.Serial(serial_port,
                     baudrate=baud_rate,
                     timeout=5.0,
                     bytesize=8,
                     parity='N',
                     stopbits=1)

# mqtt_client = mqtt_publisher.connect()

try:
    while True:
        # Read until the start of the header (0xA5)
        header_byte1 = ser.read()
        if header_byte1 == b'\xA5':
            # Once the first header byte is found, check the second header byte
            header_byte2 = ser.read()
            if header_byte2 == b'\x5A':
                # Reading the command
                cmd_data = ser.read()
                # Read the remaining 14 bytes of data
                data = ser.read(13)
                # Combine header bytes and data
                packet = header_byte1 + header_byte2 + cmd_data + data

                # Parsing Data
                if(cmd_data == b'\x01'):
                    data_parser.parse_pc_ping_response_packet(packet)
                elif(cmd_data == b'\x02'):
                    data_parser.parse_BNO08X_packet(packet)
                elif(cmd_data == b'\x03'):
                    data_parser.parse_Encoder_Package_packet(packet)
                elif(cmd_data == b'\x04'):
                    data_parser.parse_Sensor_packet(packet)
                elif(cmd_data == b'\x05'):
                    data_parser.parse_Kinematic_packet(packet)    
                elif(cmd_data == b'\x06'):
                    data_parser.parse_DWM_packet(packet)  

                # Convert Data to String
                parsed_data = "".join("{:02X}".format(byte) for byte in packet)
                # Send Data to MQTT
                # mqtt_publisher.publish(mqtt_client,parsed_data) 

except KeyboardInterrupt:
    # Close the serial port when Ctrl+C is pressed
    ser.close()
