import serial
import testing_parser
from datetime import datetime


# Define the serial port and baudrate
serial_port = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A50285BI-if00-port0'  # or 'COM1' for Windows
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
    # Prompt the user for input and read it
    file_name = input("Enter File Name: ")

    # mqtt_subscriber.subscribe(mqtt_client,ser)
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
                data = ser.read(16)
                # Combine header bytes and data
                packet = header_byte1 + header_byte2 + cmd_data + data

                # Parsing Data
                if(cmd_data == b'\x01'):
                    data_parsing = testing_parser.parse_pc_ping_response_packet(packet)
                elif(cmd_data == b'\x02'):
                    data_parsing = testing_parser.parse_BNO08X_packet(packet)
                elif(cmd_data == b'\x03'):
                    data_parsing = testing_parser.parse_Encoder(packet)
                elif(cmd_data == b'\x04'):
                    data_parsing = testing_parser.parse_Sensor_packet(packet)
                elif(cmd_data == b'\x05'):
                    data_parsing = testing_parser.parse_Kinematic_packet(packet)    
                elif(cmd_data == b'\x06'):
                    data_parsing = testing_parser.parse_Encoder(packet) 
                elif(cmd_data == b'\x15'):
                    data_parsing = testing_parser.parse_Odometry_packet(packet)  

                # Get the current time
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Log the data to a text file with the current time
                with open(f'data/{file_name}.txt', 'a') as file:
                    file.write(f"{current_time} {data_parsing}\n")

                print(f"{current_time} {data_parsing}")
                

except KeyboardInterrupt:
    # Close the serial port when Ctrl+C is pressed
    ser.close()
