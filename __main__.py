import cantools
import can
import sys

import paho.mqtt.client as mqtt


# The callback for when the client receives a CONNACK response from the server.
def onConnectMQTT(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def onMessageMQTT(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")


def systemCAN_ReceiveMessage(msg):
    pass

def main():
    # Initialize MQTT Client
    mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttClient.on_connect = onConnectMQTT
    mqttClient.on_message = onMessageMQTT

    if mqttClient.connect("localhost", 1883, 60) != 0:
        print("Could not connect to MQTT Broker!")
        sys.exit(-1)
    
    # Initialize CAN-BUS
    systemCAN_Bus = can.interface.Bus('can0', bustype='socketcan', bitrate=250000)
    systemCAN_Printer = can.Printer()

    systemCAN_Bus_Notifier = can.Notifier(systemCAN_Bus, [systemCAN_Printer, systemCAN_ReceiveMessage])

    
    mqttClient.subscribe("test/ping")

    try:
        print("Press CTRL+C to exit...")
        mqttClient.loop_forever()
    except:
        systemCAN_Bus_Notifier.stop()
        print("Disconnecting from broker")

    mqttClient.disconnect()

    



if __name__ == "__main__":
    main()