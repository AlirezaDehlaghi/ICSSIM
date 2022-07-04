from ics_sim.Device import PLC, SensorConnector, ActuatorConnector
from Configs import TAG, Controllers, Connection
import logging


class PLC1(PLC):
    def __init__(self):
        sensor_connector = SensorConnector(Connection.CONNECTION)
        actuator_connector = ActuatorConnector(Connection.CONNECTION)
        super().__init__(1, sensor_connector, actuator_connector, TAG.TAG_LIST, Controllers.PLCs)

    def _logic(self):
        #  update TAG.TAG_TANK_INPUT_VALVE_STATUS

        if not self._check_manual_input(TAG.TAG_TANK_INPUT_VALVE_MODE, TAG.TAG_TANK_INPUT_VALVE_STATUS):
            tank_level = self._get(TAG.TAG_TANK_LEVEL_VALUE)
            if tank_level > self._get(TAG.TAG_TANK_LEVEL_MAX):
                self._set(TAG.TAG_TANK_INPUT_VALVE_STATUS, 0)
            elif tank_level < self._get(TAG.TAG_TANK_LEVEL_MIN):
                self._set(TAG.TAG_TANK_INPUT_VALVE_STATUS, 1)

        #  update TAG.TAG_TANK_OUTPUT_VALVE_STATUS
        if not self._check_manual_input(TAG.TAG_TANK_OUTPUT_VALVE_MODE, TAG.TAG_TANK_OUTPUT_VALVE_STATUS):
            bottle_level = self._get(TAG.TAG_BOTTLE_LEVEL_VALUE)
            belt_position = self._get(TAG.TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE)
            if bottle_level > self._get(TAG.TAG_BOTTLE_LEVEL_MAX) or belt_position > 1.0:
                self._set(TAG.TAG_TANK_OUTPUT_VALVE_STATUS, 0)
            else:
                self._set(TAG.TAG_TANK_OUTPUT_VALVE_STATUS, 1)

    def _post_logic_update(self):
        super()._post_logic_update()
        #self.report("{} {}".format( self.get_alive_time() / 1000, self.get_loop_latency() / 1000), logging.INFO)


if __name__ == '__main__':
    plc1 = PLC1()
    plc1.set_record_variables(True)
    plc1.start()
