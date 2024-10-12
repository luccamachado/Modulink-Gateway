import cantools
import can

import paho.mqtt.client as mqtt





def systemCAN_ReceiveMessage():
    pass

def main():
    systemCAN_Bus = can.Bus('can0', bustype='socketcan', bitrate=250000)
    systemCAN_Printer = can.Printer()

    systemCAN_Bus_Notifier = can.Notifier(systemCAN_Bus, [systemCAN_Printer, systemCAN_ReceiveMessage])

    input(f"Press any key to exit...")

    



if __name__ == "__main__":
    main()