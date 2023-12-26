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

from ics_sim.Attacks import _do_scan_scapy_attack, _do_replay_scapy_attack, _do_mitm_scapy_attack, \
    _do_scan_nmap_attack, _do_command_injection_attack, _do_ddos_attack


class AttackerBase(Runnable, ABC):
    def __init__(self, name1):
        Runnable.__init__(self, name1, 100)

    def _before_start(self):
        Runnable._before_start(self)

        self.attack_path = os.path.join('.', 'attacks')
        self.log_path = os.path.join('.', 'logs', 'attack-logs')
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        self.MAC = Ether().src
        self.IP = get_if_addr(conf.iface)

        self.attack_history = self.setup_logger(
            f'{self.name()}_summary',
            logging.Formatter('%(message)s'),
            file_dir=self.log_path,
            file_ext='.csv'
        )

        self.attack_history.info(
            "{},{},{},{},{},{},{},{}"
            .format("attack", "startStamp", "endStamp", "startTime", "endTime", "attackerMAC", "attackerIP",
                    "description")
        )

        self.attack_list = {
            # 'scan-ettercap': 'ip-scan',
            # 'scan-ping': 'ip-scan',
            'scan-nmap': 'port-scan',
            'scan-scapy': 'ip-scan',
            'mitm-scapy': 'mitm',
            # 'mitm-ettercap': 'mitm',
            'ddos': 'ddos',
            'replay-scapy': 'replay',
            'command-injection': 'command-injection'}

        self.attack_cnt = len(self.attack_list)

    def _old_apply_attack(self, short_name, full_name):
        # todo: we may remote this function in future.
        attack_path = os.path.join(self.attack_path, str(full_name) + ".sh")

        if not os.path.isfile(attack_path):
            raise ValueError('command {} does not exist'.format(attack_path))

        self.report(self._make_text('running ' + attack_path, self.COLOR_YELLOW))
        log_file = os.path.join(self.log_path, "log-{}.txt".format(full_name))
        start_time = datetime.now()

        # todo: changed for test
        if full_name == "scan-scapy":
            _do_scan_scapy_attack(self.log_path, log_file)
        else:
            subprocess.run([attack_path, self.log_path, log_file])

    def _apply_attack(self, short_name, full_name):

        log_file = os.path.join(self.log_path, f'log-{full_name}.txt')
        start_time = datetime.now()
        self._do_sample_attack(full_name, self.log_path, log_file)
        end_time = datetime.now()

        wait_time = 5	
        if full_name == 'ddos':
            start_time = start_time + timedelta(seconds=5)
            wait_time = 40

        self.attack_history.info(
            "{},{},{},{},{},{},{},{}".format(
                short_name, start_time.timestamp(), end_time.timestamp(), start_time, end_time, self.MAC, self.IP,
                full_name
            )
        )
        self.report(f'applied {full_name} attack successfully.')

        self.report(f'waiting {wait_time} seconds to cooldown attack')
        sleep(wait_time)

    @staticmethod
    def _do_sample_attack(name, log_dir, log_file):
        if name == "scan-scapy":
            _do_scan_scapy_attack(log_dir, log_file, destination='192.168.0.1/24', timeout=10)
        elif name == "replay-scapy":
            _do_replay_scapy_attack(log_dir, log_file, timeout=15, replay_count=3,
                                    destination='192.168.0.11,192.168.0.22')

        elif name == "mitm-scapy":
            #_do_mitm_scapy_attack(log_dir, log_file, timeout=15, noise=0.2, destination='192.168.0.11,192.168.0.21')
            _do_mitm_scapy_attack(log_dir, log_file, timeout=30, noise=0.1, destination='192.168.0.1/24')
        elif name == "scan-nmap":
            _do_scan_nmap_attack(log_dir, log_file, destination='192.168.0.1-255')
        elif name == "command-injection":
            _do_command_injection_attack(log_dir, log_file, 'CommandInjectionAgent.py', command_counter=30)
        elif name == "ddos":
            _do_ddos_attack(log_dir, log_file, 'DDosAgent.py', 10, destination='192.168.0.11')
        else:
            print("Attack not found")
