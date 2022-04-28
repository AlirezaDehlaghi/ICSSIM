from pyModbusTCP.server import ModbusServer

from HMI1 import HMI1
from FactorySimulation import FactorySimulation
from PLC1 import PLC1
from PLC2 import PLC2
import memcache
from Configs import Connection, TAG

from ics_sim.protocol import ProtocolFactory
from ics_sim.connectors import FileConnector, ConnectorFactory

"""
factory = FactorySimulation()
factory.start()


plc1 = PLC1()
plc1.start()


plc2 = PLC2()
plc2.start()
"""

connector = ConnectorFactory.build(Connection.File_CONNECTION)
print(connector.get('ali'))
#connector.initialize({'ali':10})







