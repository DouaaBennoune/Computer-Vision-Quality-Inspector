from pyModbusTCP.client import ModbusClient

c = ModbusClient(host="192.168.100.18", port=502, auto_open=True)
result = c.write_single_coil(0, True)
print("Write result:", result)

coils = c.read_coils(0, 1)
print("Coil 0 value:", coils)