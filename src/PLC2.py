import logging
import time

from ics_sim.Device import PLC, SensorConnector, ActuatorConnector
from Configs import TAG, Connection, Controllers


class PLC2(PLC):
    def __init__(self):
        sensor_connector = SensorConnector(Connection.CONNECTION)
        actuator_connector = ActuatorConnector(Connection.CONNECTION)
        super().__init__(2, sensor_connector, actuator_connector, TAG.TAG_LIST, Controllers.PLCs)

    def _logic(self):
        if not self._check_manual_input(TAG.TAG_CONVEYOR_BELT_ENGINE_MODE, TAG.TAG_CONVEYOR_BELT_ENGINE_STATUS):
            t1 = time.time()
            flow = self._get(TAG.TAG_TANK_OUTPUT_FLOW_VALUE)

            belt_position = self._get(TAG.TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE)
            bottle_level = self._get(TAG.TAG_BOTTLE_LEVEL_VALUE)

            if (belt_position > 1) or (flow == 0 and bottle_level > self._get(TAG.TAG_BOTTLE_LEVEL_MAX)):
                self._set(TAG.TAG_CONVEYOR_BELT_ENGINE_STATUS, 1)
            else:
                self._set(TAG.TAG_CONVEYOR_BELT_ENGINE_STATUS, 0)


if __name__ == '__main__':
    plc2 = PLC2()
    plc2.set_record_variables(True)
    plc2.start()
