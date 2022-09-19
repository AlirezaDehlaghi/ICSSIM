import logging
import os
import random
import subprocess
from datetime import datetime, timedelta
from time import sleep

from scapy.arch import get_if_addr
from scapy.config import conf
from scapy.layers.l2 import Ether

from ics_sim.Device import Runnable


class AttackerMachine(Runnable):
    def __init__(self):
        Runnable.__init__(self, 'AttackerMachine', 100)

    def _before_start(self):
        Runnable._before_start(self)

        self.__attack_path = './attacks'
        self.__log_path = os.path.join(self.__attack_path, 'attack-logs')

        self.MAC = Ether().src
        self.IP = get_if_addr(conf.iface)

        if not os.path.exists(self.__log_path):
            os.makedirs(self.__log_path)

        self.__log_attack_summary = self.setup_logger(
            "attacker_machine_summary",
            logging.Formatter('%(message)s'),
            file_dir=self.__log_path,
            file_ext='.csv'
        )

        self.__log_attack_summary.info("{},{},{},{},{},{},{},{}".format("attack",
                                                                        "startStamp",
                                                                        "endStamp",
                                                                        "startTime",
                                                                        "endTime",
                                                                        "attackerMAC",
                                                                        "attackerIP",
                                                                        "description"
                                                                        )
                                       )

        self.__attack_list = {'scan-ettercap': 'ip-scan',
                              'scan-ping': 'ip-scan',
                              'scan-nmap': 'port-scan',
                              'scan-scapy': 'ip-scan',
                              'mitm-scapy': 'mitm',
                              'mitm-ettercap': 'mitm',
                              'ddos': 'ddos',
                              'replay-scapy': 'replay'}

        self.__attack_scenario = []
        self.__attack_scenario += ['scan-ettercap'] * 0  # this should be 0, cannot automate
        self.__attack_scenario += ['scan-ping'] * 0
        self.__attack_scenario += ['scan-nmap'] * 18
        self.__attack_scenario += ['scan-scapy'] * 24
        self.__attack_scenario += ['mitm-scapy'] * 16
        self.__attack_scenario += ['mitm-ettercap'] * 0
        self.__attack_scenario += ['ddos'] * 8
        self.__attack_scenario += ['replay-scapy'] * 8

        random.shuffle(self.__attack_scenario)

        self.__attack_cnt = len(self.__attack_list)

    def _logic(self):
        while True:
            response = input("Do you want to start attacks? \n")
            response = response.lower()
            if response == 'y' or response == 'yes':
                self._set_clear_scr(False)
                break
            else:
                continue

        self.report('Attacker Machine start to apply {} attacks'.format(len(self.__attack_scenario)))
        self.__status_board = {}

        for attack_name in self.__attack_scenario:
            try:
                attack_short_name = self.__attack_list[attack_name]
                attack_path = os.path.join(self.__attack_path, str(attack_name) + ".sh")

                if not self.__status_board.keys().__contains__(attack_name):
                    self.__status_board[attack_name] = 0
                self.__status_board[attack_name] += 1

                if not os.path.isfile(attack_path):
                    raise ValueError('command {} does not exist'.format(attack_path))

                self.report(self._make_text('running ' + attack_path, self.COLOR_YELLOW))
                log_file = os.path.join(self.__log_path, "log-{}.txt".format(attack_name))
                start_time = datetime.now()
                subprocess.run([attack_path, self.__log_path, log_file])
                end_time = datetime.now()

                if attack_name == 'ddos':
                    start_time = start_time + timedelta(seconds=5)

                self.__log_attack_summary.info("{},{},{},{},{},{},{},{}".format(attack_short_name,
                                                                                start_time.timestamp(),
                                                                                end_time.timestamp(),
                                                                                start_time,
                                                                                end_time,
                                                                                self.MAC,
                                                                                self.IP,
                                                                                attack_name,
                                                                                )
                                               )
                for attack in self.__status_board.keys():
                    text = '{}: applied {} times'.format(attack, self.__status_board[attack])
                    self.report(self._make_text(text, self.COLOR_GREEN))

                self.report('waiting 30 seconds')
                sleep(30)

            except ValueError as e:
                self.report(e.__str__())

            except Exception as e:
                self.report('The input is invalid ' + e.__str__())

        input('press inter to continue ...')


if __name__ == '__main__':
    attackerMachine = AttackerMachine()
    attackerMachine.start()
