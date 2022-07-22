from scapy.all import *


class ModbusTCP(Packet):
    name = "modbus_tcp"
    fields_desc = [ShortField("TransID", 0),
                   ShortField("ProtocolID", 0),
                   ShortField("Length", 0),
                   ByteField("UnitID", 0)
                   ]


class ModbusWriteRequest(Packet):
    name = "modbus_tcp_write"
    fields_desc = [ByteField("Command", 0),
                   ShortField("Reference", 0),
                   ShortField("WordCnt", 0),
                   ByteField("ByteCnt", 0),
                   ShortField("Data0", 0),
                   ShortField("Data1", 0),
                   ]


class ModbusReadRequestOrWriteResponse(Packet):
    name = "modbus_tcp_read_request"
    fields_desc = [ByteField("Command", 0),
                   ShortField("Reference", 0),
                   ShortField("WordCnt", 0),
                   ]


class ModbusReadResponse(Packet):
    name = "modbus_tcp_read_response"
    fields_desc = [ByteField("Command", 0),
                   ByteField("ByteCnt", 0),
                   ShortField("Data0", 0),
                   ShortField("Data1", 0),
                   ]
