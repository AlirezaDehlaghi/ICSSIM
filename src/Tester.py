from pyModbusTCP.server import ModbusServer, DataBank
data_bank = DataBank()
server = ModbusServer('127.0.0.1', 5001, data_bank)
server.start()
server.data_bank.set_holding_registers(3,[5,6])
DataBank.set_holding_registers(server.data_bank,4,[4])

print(server.data_bank.get_holding_registers(2,3))





