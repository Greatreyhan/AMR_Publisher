import keyboard
import mqtt_publisher
import serial
import data_parser
import time

# Define the serial port and baudrate
serial_port = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A50285BI-if00-port0'  # or 'COM1' for Windows
baud_rate = 115200

ser = serial.Serial(serial_port,
                    baudrate=baud_rate,
                    timeout=5.0,
                    bytesize=8,
                    parity='N',
                    stopbits=1)

id_cmd = 1

print('connecting...')
client = mqtt_publisher.connect_mqtt()

def get_numeric_input():
    num_str = ""
    print("", end="", flush=True)
    while True:
        key = keyboard.read_event()
        if key.event_type == keyboard.KEY_DOWN:
            if key.name.isdigit():
                num_str += key.name
                print(key.name, end="", flush=True)
            elif key.name == "enter":
                print()
                return int(num_str) if num_str else 0

def connect():
    print('connecting...')
    mqtt_publisher.run()

def farewell():
    print("Goodbye!")

def arrow_up_action():
    global id_cmd
    print('Move Forward')
    data_parser.send_command(ser,id_cmd,0,100,0)    
    id_cmd+=1


def arrow_down_action():
    global id_cmd
    print("Move Backward")
    data_parser.send_command(ser,id_cmd,0,-100,0)   
    id_cmd+=1

def arrow_left_action():
    global id_cmd
    print("Move Left")
    data_parser.send_command(ser,id_cmd,-100,0,0)   
    id_cmd+=1

def arrow_right_action():
    global id_cmd
    print("Move Right")
    data_parser.send_command(ser,id_cmd,100,0,0)   
    id_cmd+=1

def act_up():
    global id_cmd
    print("Actuator Up")
    command_id_str = f"{id_cmd:02}"  # Format id_cmd as a two-digit string
    data_parser.parse_Command(f'AA55{command_id_str}0000001000000',ser)
    id_cmd += 1

def act_down():
    global id_cmd
    print(f"Actuator Up")
    command_id_str = f"{id_cmd:02}"  # Format id_cmd as a two-digit string
    data_parser.parse_Command(f'AA55{command_id_str}0000002000000',ser)
    id_cmd += 1

def act_box():
    print("Box Detected!")
    mqtt_publisher.publish(client, "A55A21021P00P02P01P02")

def act_box_double():
    print("Box Detected!")
    mqtt_publisher.publish(client, "A55A21041P00P02P00P03P01P02P01P03")

def act_human():
    print("Human Detected!")
    mqtt_publisher.publish(client, "A55A21041P00P02P00P03P01P02P01P03")

def edit_position():
    print("Enter X Position:")
    val_x = get_numeric_input()
    print("Enter Y Position:")
    val_y = get_numeric_input()
    mqtt_publisher.publish(client, f"A55A15{val_x:02X}00{val_y:02X}000000FF")

def test_human():
    global id_cmd
    print('Move Forward')
    data_parser.send_command(ser,id_cmd,0,100,0)    
    id_cmd+=1
    time.sleep(5)
    print("Human Detected!")
    mqtt_publisher.publish(client, "A55A21061P00P02P00P03P01P02P01P03N01P02N01P03")

def main():
    command_dict = {
        'c': connect,
        'f': farewell,
        'up': arrow_up_action,
        'down': arrow_down_action,
        'left': arrow_left_action,
        'right': arrow_right_action,
        'j' : act_up,
        'k' : act_down,
        'b' : act_box,
        'h' : act_human,
        'd' : act_box_double,
        'p' : edit_position,
        't' : test_human
    }

    key_states = {
        'c': False,
        'f': False,
        'up': False,
        'down': False,
        'left': False,
        'right': False,
        'j': False,
        'k' : False,
        'b' : False,
        'h' : False,
        'd' : False,
        'p' : False,
        't' : False,
    }

    print("Press command key. Press 'esc' to quit.")

    while True:
            if keyboard.is_pressed('esc'):
                break

            for key in key_states.keys():
                if keyboard.is_pressed(key) and not key_states[key]:
                    key_states[key] = True
                    command_dict[key]()
                elif not keyboard.is_pressed(key) and key_states[key]:
                    key_states[key] = False

            time.sleep(0.1)  # Sleep to reduce CPU usage

if __name__ == "__main__":
    main()
