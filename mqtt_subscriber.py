# python 3.11
import serial
import random
import data_parser

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

        msg = input_message.payload.decode()
        print(msg)
        
        if(msg[:2] == 'AA'):
            data_parser.parse_MQTT_Coordinate(msg,serial)
        elif(msg[:4] == 'A55A'):
            data_parser.parse_MQTT_Astar(msg,serial)

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
