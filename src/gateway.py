from pyModbusTCP.client import ModbusClient
import paho.mqtt.client as mqtt
import json

# Connect to Factory 
modbus_client = ModbusClient(host="192.168.100.18", port=502, auto_open=True)
def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to Docker MQTT Broker!")
    client.subscribe("factory/line1/control")
    modbus_client.write_single_coil(0, True)
    modbus_client.write_single_coil(1, True)
    print("Conveyor Belt STARTED.")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    command = payload.get("command")
    
    if command == "STOP_CONVEYOR":
        print(f"AI ALARM: {payload.get('reason')} -> Stopping Conveyor")
        modbus_client.write_single_coil(0, False) # Stop Motor
        modbus_client.write_single_coil(1, False)
    elif command == "RESUME_CONVEYOR":
        modbus_client.write_single_coil(0, True)  # Start Motor
        modbus_client.write_single_coil(1, True)
# Connect to Docker Mosquitto Broker
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

print("Booting up IIoT Gateway...")
mqtt_client.connect("127.0.0.1", 1883, 60)
mqtt_client.loop_forever()