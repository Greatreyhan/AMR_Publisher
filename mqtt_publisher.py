# python 3.11
import random
import time
import serial
import data_parser

from paho.mqtt import client as mqtt_client


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


broker = 'broker.emqx.io'
port = 1883
topic = "astar/amrparams"

# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client,message):
    while True:
        msg = f"messages: {message}"
        result = client.publish(topic, message)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        break

def connect():
    client = connect_mqtt()
    client.loop_start()
    return client

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    mqtt_client = connect()

    try:
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
                    # Read the remaining 17 bytes of data
                    data = ser.read(16)
                    # Combine header bytes and data
                    packet = header_byte1 + header_byte2 + cmd_data + data

                    # Parsing Data
                    if(cmd_data == b'\x01'):
                        data_parser.parse_pc_ping_response_packet(packet)
                        # Convert Data to String
                        parsed_data = "".join("{:02X}".format(byte) for byte in packet)
                        # Send Data to MQTT
                        publish(mqtt_client,parsed_data) 
                    elif(cmd_data == b'\x02'):
                        data_parser.parse_BNO08X_packet(packet)
                        # Convert Data to String
                        parsed_data = "".join("{:02X}".format(byte) for byte in packet)
                        # Send Data to MQTT
                        publish(mqtt_client,parsed_data)
                    elif(cmd_data == b'\x03'):
                        data_parser.parse_Encoder_Package_packet(packet)
                        # Convert Data to String
                        parsed_data = "".join("{:02X}".format(byte) for byte in packet)
                        # Send Data to MQTT
                        publish(mqtt_client,parsed_data)
                    elif(cmd_data == b'\x04'):
                        data_parser.parse_Sensor_packet(packet)
                        # Convert Data to String
                        parsed_data = "".join("{:02X}".format(byte) for byte in packet)
                        # Send Data to MQTT
                        publish(mqtt_client,parsed_data)
                    elif(cmd_data == b'\x05'):
                        data_parser.parse_Kinematic_packet(packet)
                        # Convert Data to String
                        parsed_data = "".join("{:02X}".format(byte) for byte in packet)
                        # Send Data to MQTT
                        publish(mqtt_client,parsed_data)    
                    elif(cmd_data == b'\x15'):
                        data_parser.parse_Odometry_packet(packet)
                        # Convert Data to String
                        parsed_data = "".join("{:02X}".format(byte) for byte in packet)
                        # Send Data to MQTT
                        publish(mqtt_client,parsed_data)  

                    
    except KeyboardInterrupt:
        # Close the serial port when Ctrl+C is pressed
        ser.close()

