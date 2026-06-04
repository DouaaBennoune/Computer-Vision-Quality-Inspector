from pyModbusTCP.client import ModbusClient
import paho.mqtt.client as mqtt
import json
import time

# connect to Factory 
modbus_client = ModbusClient(host="192.168.100.18", port=502, auto_open=True)
def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to Docker MQTT Broker!")
    client.subscribe("factory/line1/control")
    modbus_client.write_single_coil(0, True)
    modbus_client.write_single_coil(1, True)
    print("Conveyor Belt STARTED.")
machine_latched=False
def on_message(client, userdata, msg):
    global machine_latched
    payload = json.loads(msg.payload.decode())
    command = payload.get("command")
    
    if command == "STOP_CONVEYOR":
        if not machine_latched:
             print(f"AI ALARM: {payload.get('reason')} -> Stopping Conveyor")
        machine_latched=True
        
    elif command == "RESET_LATCH":
        machine_latched=False

    if machine_latched == True:
        modbus_client.write_single_coil(0, False) # stop Motor
        modbus_client.write_single_coil(1, False)
    else:
        modbus_client.write_single_coil(0, True)  
        modbus_client.write_single_coil(1, True)      
# connect to docker Mosquitto Broker
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

print("Booting up IIoT Gateway...")
mqtt_client.connect("127.0.0.1", 1883, 60)

try:
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("\nShutting down gateway...")
    mqtt_client.disconnect()
