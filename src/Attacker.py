import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from time import sleep

from scapy.arch import get_if_addr
from scapy.config import conf
from scapy.layers.inet import IP
from scapy.layers.l2 import ARP, Ether

from ics_sim.Device import Runnable, HMI


class Attacker(Runnable):
    def __init__(self):
        Runnable.__init__(self, 'Attacker', 100)

    def _before_start(self):
        Runnable._before_start(self)
        self.__attack_path = './attacks'
        self.__log_path = os.path.join(self.__attack_path,'attack-logs')

        self.MAC = Ether().src
        self.IP = get_if_addr(conf.iface)

        if not os.path.exists(self.__log_path):
            os.makedirs(self.__log_path)

        self.__log_attack_summary = self.setup_logger(
            "attacker_summary",
            logging.Formatter('%(message)s'),
            file_dir= self.__log_path,
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
                              'replay-scapy': 'replay',
                              'command-injection':'command-injection'}

        self.__attack_cnt = len(self.__attack_list)

        pass

    def __get_menu_line(self, template, number, text):
        return template.format(
            self._make_text(str(number)+')', self.COLOR_BLUE),
            self._make_text(text, self.COLOR_YELLOW),
            self._make_text(str(number), self.COLOR_BLUE)
        )

    def _logic(self):
        menu = "\n"
        menu += self.__get_menu_line('{} to {} press {} \n', 0, 'clear')
        i = 0
        for attack in self.__attack_list.keys():
            i += 1
            menu += self.__get_menu_line('{} To apply the {} attack press {} \n', i , attack)
        self.report(menu)

        try:
            attack_name = int(input('your choice (1 to {}): '.format(self.__attack_cnt)))

            if int(attack_name) == 0:
                os.system('clear')
                return

            if 0 < attack_name <= self.__attack_cnt:
                attack_name = list(self.__attack_list.keys())[attack_name-1]
                attack_short_name = self.__attack_list[attack_name]


            attack_path = os.path.join(self.__attack_path, str(attack_name) + ".sh")

            if not os.path.isfile(attack_path):
                raise ValueError('command {} does not exist'.format(attack_path))

            self.report('running ' + attack_path)
            log_file = os.path.join(self.__log_path,"log-{}.txt".format(attack_name))
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




        except ValueError as e:
            self.report(e.__str__())

        except Exception as e:
            self.report('The input is invalid ' + e.__str__())

        input('press inter to continue ...')


if __name__ == '__main__':
    attacker = Attacker()
    attacker.start()
