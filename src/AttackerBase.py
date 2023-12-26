import os
from abc import ABC
from time import sleep

from scapy.arch import get_if_addr
from scapy.config import conf
from scapy.layers.l2 import Ether
from datetime import datetime, timedelta
from ics_sim.Device import Runnable
import logging
import subprocess

from attacks.Attacks import _do_scan_scapy_attack


class AttackerBase(Runnable, ABC):
    def __init__(self, name1):
        Runnable.__init__(self, name1, 100)

    def _before_start(self):
        Runnable._before_start(self)

        self.attack_path = os.path.join('.', 'attacks')
        self.log_path = os.path.join(self.attack_path, 'attack-logs')

        self.MAC = Ether().src
        self.IP = get_if_addr(conf.iface)

        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        self.log_attack_summary = self.setup_logger(
            f'{self.name()}_summary',
            logging.Formatter('%(message)s'),
            file_dir=self.log_path,
            file_ext='.csv'
        )

        self.log_attack_summary.info("{},{},{},{},{},{},{},{}".format("attack",
                                                                      "startStamp",
                                                                      "endStamp",
                                                                      "startTime",
                                                                      "endTime",
                                                                      "attackerMAC",
                                                                      "attackerIP",
                                                                      "description"
                                                                      )
                                     )

        self.attack_list = {'scan-ettercap': 'ip-scan',
                            'scan-ping': 'ip-scan',
                            'scan-nmap': 'port-scan',
                            'scan-scapy': 'ip-scan',
                            'mitm-scapy': 'mitm',
                            'mitm-ettercap': 'mitm',
                            'ddos': 'ddos',
                            'replay-scapy': 'replay',
                            'command-injection': 'command-injection'}

        self.attack_cnt = len(self.attack_list)

    def _apply_attack(self, short_name, full_name):

        attack_path = os.path.join(self.attack_path, str(full_name) + ".sh")

        if not os.path.isfile(attack_path):
            raise ValueError('command {} does not exist'.format(attack_path))

        self.report(self._make_text('running ' + attack_path, self.COLOR_YELLOW))
        log_file = os.path.join(self.log_path, "log-{}.txt".format(full_name))
        start_time = datetime.now()

        #todo: changed for test
        if full_name == "scan-scapy":
            _do_scan_scapy_attack(self.log_path, log_file)
        else:
            subprocess.run([attack_path, self.log_path, log_file])






        end_time = datetime.now()

        if full_name == 'ddos':
            start_time = start_time + timedelta(seconds=5)

        self.log_attack_summary.info("{},{},{},{},{},{},{},{}".format(short_name,
                                                                      start_time.timestamp(),
                                                                      end_time.timestamp(),
                                                                      start_time,
                                                                      end_time,
                                                                      self.MAC,
                                                                      self.IP,
                                                                      full_name
                                                                      )
                                     )
        self.report(f'applied {full_name} attack successfully.')

        self.report('waiting 40 seconds to cooldown attack')
        sleep(40)

