from pyModbusTCP.client import ModbusClient
from pyModbusTCP.server import ModbusServer, DataBank


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def receive(self, tag_id):
        pass

    def send(self, tag_id, value):
        pass


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def start(self):
        pass

    def stop(self):
        pass

    def set(self, tag_id, value):
        pass

    def get(self, tag_id):
        pass


class ModbusBase:
    def __init__(self, word_num=2, precision=4):
        self._precision = precision
        self._word_num = word_num
        self._precision_factor = pow(10, precision)
        self._base = pow(2, 16)
        self._max_int = pow(self._base, word_num)

    def decode(self, word_array):

        if len(word_array) != self._word_num:
            raise ValueError('word array length is not correct')

        base_holder = 1
        result = 0

        for word in word_array:
            result *= base_holder
            result += word
            base_holder *= self._base

        return result / self._precision_factor

    def encode(self, number):

        number = int(number * self._precision_factor)

        if number > self._max_int:
            raise ValueError('input number exceed max limit')

        result = []
        while number:
            result.append(number % self._base)
            number = int(number / self._base)

        while len(result) < self._word_num:
            result.append(0)

        result.reverse()
        return result

    def get_registers(self, index):
        return index * self._word_num


class ClientModbus(Client, ModbusBase):
    def __init__(self, ip, port):
        ModbusBase.__init__(self)
        Client.__init__(self, ip, port)
        self.client = ModbusClient(host=self.ip, port=self.port)

    def receive(self, tag_id):
        self.open()
        return self.decode(self.client.read_holding_registers(self.get_registers(tag_id), self._word_num))

    def send(self, tag_id, value):
        self.open()
        self.client.write_multiple_registers(self.get_registers(tag_id), self.encode(value))

    def open(self):
        if not self.client.is_open:
            self.client.open()

    def close(self):
        if self.client.is_open:
            self.client.close()


class ServerModbus(Server, ModbusBase):
    def __init__(self, ip, port):
        ModbusBase.__init__(self)
        Server.__init__(self, ip, port)
        self.server = ModbusServer(ip, port, no_block=True)

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    def set(self, tag_id, value):
        self.server.data_bank.set_holding_registers(self.get_registers(tag_id),self.encode(value))
        #DataBank.set_words(self.get_registers(tag_id), self.encode(value))

    def get(self, tag_id):
        return self.decode(self.server.data_bank.get_holding_registers(self.get_registers(tag_id), self._word_num))
        #return self.decode(DataBank.get_words(self.get_registers(tag_id), self._word_num))



class ProtocolFactory:
    @staticmethod
    def create_client(protocol, ip, port):
        if protocol == 'ModbusWriteRequest-TCP':
            return ClientModbus(ip, port)
        else:
            raise TypeError()

    @staticmethod
    def create_server(protocol, ip, port):
        if protocol == 'ModbusWriteRequest-TCP':
            return ServerModbus(ip, port)
        else:
            raise TypeError()
