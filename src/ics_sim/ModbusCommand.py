from datetime import datetime

from protocol import ClientModbus


class ModbusCommand:
    clients = dict()

    command_write_multiple_registers = 16
    command_read_holding_registers = 3

    def __init__(self, sip, dip, port, command, tag, value, new_value, word_num=2):
        self.sip = sip
        self.dip = dip
        self.port = port
        self.command = command
        self.tag = int(tag)
        self.address = tag * word_num
        self.value = value
        self.time = datetime.now().timestamp()
        self.new_value = new_value

    def __str__(self):
        return 'sip:{} dip{} port:{} command:{} address:{} value:{} time:{}'.format(
            self.sip, self.dip, self.port, self.command, self.address, self.value, self.new_value ,self.time)

    def send_fake(self):
        if not ModbusCommand.clients.keys().__contains__((self.dip, self.port)):
            ModbusCommand.clients[(self.dip, self.port)] = ClientModbus(self.dip, self.port)

        client = ModbusCommand.clients[(self.dip, self.port)]

        if self.command == ModbusCommand.command_read_holding_registers:
            client.receive(self.tag)

        if self.command == ModbusCommand.command_write_multiple_registers:
            client.send(self.tag, self.value)

