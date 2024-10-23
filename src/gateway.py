#!/bin/python3

import can, cantools
import json
import sys, os

import paho.mqtt.client as mqtt

import mqtt_callbacks, mqtt_publish


MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60

CAN_CHANNEL = "can0"
CAN_INTERFACE = "socketcan"
CAN_BITRATE = 250000
CAN_DBC_FILE_NAME = "CCU.dbc"


# TODO:
# ADD SUBSCRIPTIONS CALLBACKS
# ADD JSON TOPICS CONFIGURATION FILE

topicList = None

class Gateway():
    mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    systemCAN_Bus = None
    systemCAN_Bus_Notifier = None

    systemCAN_DBC = None
    systemCAN_Protocol_Version_MQTT = None


    def __init__(self):
        super().__init__()

        # Load Topic List from JSON File
        jsonPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "topics_config.json")
        with open(jsonPath) as jsonFile:
            global topicList 
            topicList = json.load(jsonFile)
            self.systemCAN_Protocol_Version_MQTT = topicList["Protocol Version"]
            del topicList["Protocol Version"]

        # Initialize MQTT Client
        if self.mqttClient.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL) != 0:
            print("Could not connect to MQTT Broker!")
            sys.exit(-1)

        # Initialize System CAN DBC
        dbcFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"dbc/{CAN_DBC_FILE_NAME}")
        self.systemCAN_DBC = cantools.database.load_file(dbcFilePath)

        # Initialize CAN-BUS
        self.systemCAN_Bus = can.Bus(CAN_CHANNEL, interface=CAN_INTERFACE, bitrate=CAN_BITRATE)
        self.systemCAN_Bus_Notifier = can.Notifier(self.systemCAN_Bus, [self.systemCAN_ReceiveMessage])


    # The callback called when the broker reponds to our connection request.
    @mqttClient.connect_callback()
    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code: {reason_code}")

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        global topicList
        for topic in topicList:
            if topicList[topic]["type"] == "subscribe":
                # client.subscribe(topic)
                print(topicList[topic])


    # The callback called when the client failed to connect to the broker.
    @mqttClient.connect_fail_callback()
    def on_connect_fail(client):
        print(f"Failed to connect to server")
    

    # The callback called when the client disconnects from the broker.
    @mqttClient.disconnect_callback()
    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        print(f"Disconnected with result code: {reason_code}")
    

    # The callback called when the client has log information. Defined to allow debugging.
    @mqttClient.log_callback()
    def on_log(client, userdata, level, buf):
        # print(f"{level}: {buf}")
        pass
    

    # The callback called when a message has been received on a topic that the client subscribes to
    @mqttClient.message_callback()
    def on_message(client, userdata, msg):
        print(f"{msg.topic}: {msg.payload.decode()}")
    

    # The callback called immediately prior to the connection is made request.
    @mqttClient.pre_connect_callback()
    def on_pre_connect(client, userdata):
        pass
    

    # The callback called when a message that was to be sent using the publish() call has completed transmission to the broker.
    @mqttClient.publish_callback()
    def on_publish(client, userdata, mid, reason_code, properties):
        pass
    

    # The callback called when the broker responds to a subscribe request.
    @mqttClient.subscribe_callback()
    def on_subscribe(client, userdata, mid, reason_code_list, properties):
        pass
    

    # The callback called when the broker responds to a subscribe request.
    @mqttClient.unsubscribe_callback()
    def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
        pass
    

    def systemCAN_ReceiveMessage(self, msg):
        self.mqttClient.publish("SystemCAN/raw", str(msg))

        try:
            msg_name = self.systemCAN_DBC.get_message_by_frame_id(msg.arbitration_id).name
            decoded_msg = self.systemCAN_DBC.decode_message(msg.arbitration_id, msg.data)
            decoded_msg_keys = decoded_msg.keys()

            mqtt_publish.publishSystemCAN(decoded_msg, topicList)

        except Exception as e:
            print(f"CAN Message Error: {e} on message {msg}")

        
    def run(self):
        try:
            print("Press CTRL+C to exit...")
            self.mqttClient.loop_forever()
        except:
            print("Disconnecting from broker")
        
        self.systemCAN_Bus_Notifier.stop()
        self.systemCAN_Bus.shutdown()
        self.mqttClient.disconnect()



if __name__ == "__main__":
    app = Gateway()
    app.run()