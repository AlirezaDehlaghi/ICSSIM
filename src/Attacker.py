import logging
import os
import subprocess
import sys
from datetime import datetime
from time import sleep

from ics_sim.Device import Runnable, HMI


class Attacker(Runnable):
    def __init__(self):
        Runnable.__init__(self, 'Attacker', 100)

    def _before_start(self):
        Runnable._before_start(self)
        self.__attack_path = './attacks'
        self.__log_path = os.path.join(self.__attack_path,'attack-logs')

        if not os.path.exists(self.__log_path):
            os.makedirs(self.__log_path)

        self.__log_attack_summary = self.setup_logger(
            "log_summary",
            logging.Formatter('%(message)s'),
            file_dir= self.__log_path,
            file_ext='.csv'
        )

        self.__attack_list = ['scan-ettercap',
                              'scan-ping',
                              'scan-nmap',
                              'scan-scapy',
                              'mitm-scapy',
                              'mitm-ettercap',
                              'ddos',
                              'replay-scapy']

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
        for i in range(len(self.__attack_list)):
            menu += self.__get_menu_line('{} To apply the {} attack press {} \n', i + 1, self.__attack_list[i])
        self.report(menu)

        try:
            attack_name = int(input('your choice (1 to {}): '.format(len(self.__attack_list))))

            if int(attack_name) == 0:
                os.system('clear')
                return

            if 0 < attack_name <= len(self.__attack_list):
                attack_name = self.__attack_list[attack_name-1]


            attack_path = os.path.join(self.__attack_path, str(attack_name) + ".sh")
            print(os.path.isfile(attack_path))
            if not os.path.isfile(attack_path):
                raise ValueError('command {} does not exist'.format(attack_path))

            self.report('running ' + attack_path)
            log_file = os.path.join(self.__log_path,"log-{}.txt".format(attack_name))
            start_time = datetime.now()
            subprocess.run([attack_path, self.__log_path, log_file])
            end_time = datetime.now()

            self.__log_attack_summary.info("{},{},{}\n".format(attack_name, start_time, end_time))

        except ValueError as e:
            self.report(e.__str__())

        except Exception as e:
            self.report('The input is invalid ' + e.__str__())

        input('press inter to continue ...')


if __name__ == '__main__':
    attacker = Attacker()
    attacker.start()
