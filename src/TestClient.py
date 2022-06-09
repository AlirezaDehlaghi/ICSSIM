from pyModbusTCP.client import ModbusClient
client = ModbusClient(host='127.0.0.1', port=5001 )
client.open();
print( client.read_holding_registers(0))
client.rea