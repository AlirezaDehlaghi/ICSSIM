import logging

from ics_sim.Device import HIL
from Configs import TAG, PHYSICS, Connection


class FactorySimulation(HIL):
    def __init__(self):
        super().__init__('Factory', Connection.CONNECTION, 100)
        self.init()

    def _logic(self):
        elapsed_time = self._current_loop_time - self._last_loop_time

        # update tank water level
        tank_water_amount = self._get(TAG.TAG_TANK_LEVEL_VALUE) * PHYSICS.TANK_LEVEL_CAPACITY
        if self._get(TAG.TAG_TANK_INPUT_VALVE_STATUS):
            tank_water_amount += PHYSICS.TANK_INPUT_FLOW_RATE * elapsed_time

        if self._get(TAG.TAG_TANK_OUTPUT_VALVE_STATUS):
            tank_water_amount -= PHYSICS.TANK_OUTPUT_FLOW_RATE * elapsed_time

        tank_water_level = tank_water_amount / PHYSICS.TANK_LEVEL_CAPACITY

        if tank_water_level > PHYSICS.TANK_MAX_LEVEL:
            tank_water_level = PHYSICS.TANK_MAX_LEVEL
            self.report('tank water overflowed', logging.WARNING)
        elif tank_water_level <= 0:
            tank_water_level = 0
            self.report('tank water is empty', logging.WARNING)

        # update tank water flow
        tank_water_flow = 0
        if self._get(TAG.TAG_TANK_OUTPUT_VALVE_STATUS) and tank_water_amount > 0:
            tank_water_flow = PHYSICS.TANK_OUTPUT_FLOW_RATE

        # update bottle water
        if self._get(TAG.TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE) > 1:
            bottle_water_amount = 0
            if self._get(TAG.TAG_TANK_OUTPUT_FLOW_VALUE):
                self.report('water is wasting', logging.WARNING)
        else:
            bottle_water_amount = self._get(TAG.TAG_BOTTLE_LEVEL_VALUE) * PHYSICS.BOTTLE_LEVEL_CAPACITY
            bottle_water_amount += self._get(TAG.TAG_TANK_OUTPUT_FLOW_VALUE) * elapsed_time

        bottle_water_level = bottle_water_amount / PHYSICS.BOTTLE_LEVEL_CAPACITY

        if bottle_water_level > PHYSICS.BOTTLE_MAX_LEVEL:
            bottle_water_level = PHYSICS.BOTTLE_MAX_LEVEL
            self.report('bottle water overflowed', logging.WARNING)

        # update bottle position
        bottle_distance_to_filler = self._get(TAG.TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE)
        if self._get(TAG.TAG_CONVEYOR_BELT_ENGINE_STATUS):
            bottle_distance_to_filler -= elapsed_time * PHYSICS.CONVEYOR_BELT_SPEED
            bottle_distance_to_filler %= PHYSICS.BOTTLE_DISTANCE

        # update physical properties
        self._set(TAG.TAG_TANK_LEVEL_VALUE, tank_water_level)
        self._set(TAG.TAG_TANK_OUTPUT_FLOW_VALUE, tank_water_flow)
        self._set(TAG.TAG_BOTTLE_LEVEL_VALUE, bottle_water_level)
        self._set(TAG.TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE, bottle_distance_to_filler)

    def init(self):
        initial_list = []
        for tag in TAG.TAG_LIST:
            initial_list.append((tag, TAG.TAG_LIST[tag]['default']))

        self._connector.initialize(initial_list)


    @staticmethod
    def recreate_connection():
        return True


if __name__ == '__main__':
    factory = FactorySimulation()
    factory.start()
