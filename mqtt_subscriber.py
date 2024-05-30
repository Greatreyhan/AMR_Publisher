# python 3.11
import serial
import random

from paho.mqtt import client as mqtt_client

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

broker = 'broker.emqx.io'
port = 1883
topic = "astar/amrcommands"
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'
username = 'emqx'
password = 'public'

def checksum_generator(data):
    checksum = 0
    for byte in data:
        checksum += byte
    return checksum & 0xFF

def connect_mqtt() -> mqtt_client:
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


def subscribe(client: mqtt_client, serial):

    def convert_string_to_bytes(client, userdata, input_message):
        print(f"Received `{input_message.payload.decode()}` from `{input_message.topic}` topic")

        #Header Bytes
        result = [0xA5, 0x5A, 0x12]
        msg = input_message.payload.decode()

        # Check for positive/negative indicator
        pos_neg_indicator = 0x00 if msg[2] == 'P' else 0x10
        result.append(pos_neg_indicator)
        
        # Get X Position Data
        pos_x = int(msg[3:6])
        result.append(pos_x)

        # Check for positive/negative indicator
        pos_neg_indicator = 0x00 if msg[6] == 'P' else 0x10
        result.append(pos_neg_indicator)

        # Get Y Position Data
        pos_y = int(msg[7:10])
        result.append(pos_y)

        # Check for positive/negative indicator
        pos_neg_indicator = 0x00 if msg[10] == 'O' else 0x10
        result.append(pos_neg_indicator)

         # Get Y Position Data
        orient = int(msg[11:14])
        result.append(orient)

        # Check for Step
        pos_neg_indicator = 0x00 if msg[15] == 'S' else 0x73
        result.append(pos_neg_indicator)

        # Get Step Data
        step = int(msg[16:19])
        result.append(step)

        # Add Null Message
        result.append(0x00)
        result.append(0x00)
        result.append(0x00)
        result.append(0x00)

        # Add Checksum 
        chksm = checksum_generator(result)
        result.append(chksm)

        print(f"Send Data : `{bytearray(result)}`")

        serial.write(bytearray(result))


    client.subscribe(topic)
    client.on_message = convert_string_to_bytes

def subscribe_default(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client,ser)
    client.loop_forever()


if __name__ == '__main__':
    run()
