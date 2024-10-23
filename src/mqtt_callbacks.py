import paho.mqtt.client as mqtt

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)




@client.topic_callback("remoteInputs/troubleshootLevel")
def handle_troubleshootLevel(client, userdata, message):
    pass
