import time
import unittest
from ics_sim.helper import debug
from pyModbusTCP.server import ModbusServer, DataBank

from ics_sim.protocol import ClientModbus, ServerModbus, ModbusBase


class ProtocolTests(unittest.TestCase):

    def test_ModbusBase(self):
        modbus_base = ModbusBase()

        self.modbusBase_fuc(modbus_base, 0)
        self.modbusBase_fuc(modbus_base, .001)
        self.modbusBase_fuc(modbus_base, .000001)
        self.modbusBase_fuc(modbus_base, 1)
        self.modbusBase_fuc(modbus_base, 7654)
        self.modbusBase_fuc(modbus_base, 70000)

    def modbusBase_fuc(self, modbus_base, number):
        words = modbus_base.encode(number)
        new_number = modbus_base.decode(words)
        number = round(number, modbus_base._precision)
        self.assertEqual(number, new_number, 'encoding and decoding is wrong ({})'.format(number))

    def test_ModbusServer(self):
        server = ModbusServer('127.0.0.1', 5001, no_block=True)
        server.start()
        server.data_bank.set_holding_registers(5,[10])
        received = server.data_bank.get_holding_registers(5,1)[0]
        server.stop()

        self.assertEqual(10, received, 'server read write is not compatible')

    def test_ServerModbus(self):
        server = ServerModbus('127.0.0.1', 5001)
        server.start()

        self.server_modbus_func(0, 0, server)
        self.server_modbus_func(0, 10, server)
        self.server_modbus_func(0, 10.1, server)
        self.server_modbus_func(0, 10.654, server)
        self.server_modbus_func(0, 10.654321, server)

        self.server_modbus_func(5, 0, server)
        self.server_modbus_func(5, 10, server)
        self.server_modbus_func(5, 10.1, server)
        self.server_modbus_func(5, 10.654, server)
        self.server_modbus_func(5, 10.654321, server)

        server.stop()

    def server_modbus_func(self, tag_id, value, server):
        server.set(tag_id, value)
        received = server.get(tag_id)
        value = round(value, server._precision)
        self.assertEqual(value, received, 'test_ServerModbus fails on value = {}'.format(value))


    def test_client_server_modbus(self):
        client = ClientModbus('127.0.0.1', 5001)
        server = ServerModbus('127.0.0.1', 5001)
        server.start()

        self.client_server_modbus_func(server, client, 0, 10)
        self.client_server_modbus_func(server, client, 0, 0)
        self.client_server_modbus_func(server, client, 0, 1.2)
        self.client_server_modbus_func(server, client, 3, 1.2)
        self.client_server_modbus_func(server, client, 3, 7563.42)

        server.stop()
        client.close()

    def client_server_modbus_func(self, server, client, tag_id, value):
        server.set(tag_id, value)
        received = client.receive(tag_id)
        value = round(value, server._precision)
        self.assertEqual(value, received,'test_client_server_modbus fails on tag_id={} and value={}'.format(tag_id, value))


if __name__ == '__main__':
    unittest.main()