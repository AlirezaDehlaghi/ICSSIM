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

    NAME_ATTACK_SCAN_MMAP = 'scan-nmap'
    NAME_ATTACK_SCAN_SCAPY = 'scan-scapy'
    NAME_ATTACK_MITM_SCAPY = 'mitm-scapy'
    NAME_ATTACK_REPLY_SCAPY = 'replay-scapy'
    NAME_ATTACK_DDOS = 'ddos'
    NAME_ATTACK_COMMAND_INJECTION = 'command-injection'

    def __init__(self, name1):
        super().__init__(name1, 100)

        self.log_path = os.path.join('.', 'logs', 'attack-logs')
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        self.MAC = Ether().src
        self.IP = get_if_addr(conf.iface)

        self.attack_history = self.get_history_logger()

        self.attack_list = {
            # 'scan-ettercap': 'ip-scan',
            # 'scan-ping': 'ip-scan',
            AttackerBase.NAME_ATTACK_SCAN_MMAP: 'port-scan',
            AttackerBase.NAME_ATTACK_SCAN_SCAPY: 'ip-scan',
            AttackerBase.NAME_ATTACK_MITM_SCAPY: 'mitm',
            # 'mitm-ettercap': 'mitm',
            AttackerBase.NAME_ATTACK_DDOS: 'ddos',
            AttackerBase.NAME_ATTACK_REPLY_SCAPY: 'replay',
            AttackerBase.NAME_ATTACK_COMMAND_INJECTION: 'command-injection'}

    def get_history_logger(self):
        attack_history = self.setup_logger(
            f'{self.name()}_summary',
            logging.Formatter('%(message)s'),
            file_dir=self.log_path,
            file_ext='.csv'
        )

        attack_history.info(
            "{},{},{},{},{},{},{},{}"
            .format("attack", "startStamp", "endStamp", "startTime", "endTime", "attackerMAC", "attackerIP",
                    "description")
        )

        return attack_history

    def _apply_attack(self, name):
        if name == AttackerBase.NAME_ATTACK_SCAN_SCAPY:
            self._scan_scapy_attack()

        elif name == AttackerBase.NAME_ATTACK_REPLY_SCAPY:
            self._replay_scapy_attack()

        elif name == AttackerBase.NAME_ATTACK_MITM_SCAPY:
            self._mitm_scapy_attack()

        elif name == AttackerBase.NAME_ATTACK_SCAN_MMAP:
            self._scan_nmap_attack()

        elif name == AttackerBase.NAME_ATTACK_COMMAND_INJECTION:
            self._command_injection_attack()

        elif name == AttackerBase.NAME_ATTACK_DDOS:
            self._ddos_attack()
        else:
            self.report('Attack not found!')

    def _scan_scapy_attack(self, target='192.168.0.1/24', timeout=10):
        name = AttackerBase.NAME_ATTACK_SCAN_SCAPY
        log_file = os.path.join(self.log_path, f'log-{name}.txt')

        start = datetime.now()
        _do_scan_scapy_attack(log_dir=self.log_path, log_file=log_file, target=target, timeout=timeout)
        end = datetime.now()

        self._post_apply_attack(attack_name=name, start_time=start, end_time=end, post_wait_time=5)

    def _replay_scapy_attack(self, timeout=15, replay_count=3, target='192.168.0.11,192.168.0.22'):
        name = AttackerBase.NAME_ATTACK_REPLY_SCAPY
        log_file = os.path.join(self.log_path, f'log-{name}.txt')

        start = datetime.now()
        _do_replay_scapy_attack(log_dir=self.log_path, log_file=log_file, timeout=timeout, replay_count=replay_count,
                                target=target)
        end = datetime.now()

        self._post_apply_attack(attack_name=name, start_time=start, end_time=end, post_wait_time=5)

    def _mitm_scapy_attack(self, timeout=30, noise=0.1, target='192.168.0.1/24'):
        name = AttackerBase.NAME_ATTACK_MITM_SCAPY
        log_file = os.path.join(self.log_path, f'log-{name}.txt')
        start = datetime.now()

        # _do_mitm_scapy_attack(log_dir, log_file, timeout=15, noise=0.2, destination='192.168.0.11,192.168.0.21')
        _do_mitm_scapy_attack(log_dir=self.log_path, log_file=log_file, timeout=timeout, noise=noise, target=target)

        end = datetime.now()
        self._post_apply_attack(attack_name=name, start_time=start, end_time=end, post_wait_time=5)

    def _scan_nmap_attack(self, target='192.168.0.1-255'):
        name = AttackerBase.NAME_ATTACK_SCAN_MMAP
        log_file = os.path.join(self.log_path, f'log-{name}.txt')
        start = datetime.now()

        _do_scan_nmap_attack(log_dir=self.log_path, log_file=log_file, target=target)

        end = datetime.now()
        self._post_apply_attack(attack_name=name, start_time=start, end_time=end, post_wait_time=5)

    def _command_injection_attack(self, command_injection_agent='CommandInjectionAgent.py', command_counter=30):
        name = AttackerBase.NAME_ATTACK_COMMAND_INJECTION
        log_file = os.path.join(self.log_path, f'log-{name}.txt')
        start = datetime.now()

        _do_command_injection_attack(log_dir=self.log_path, log_file=log_file,
                                     command_injection_agent=command_injection_agent, command_counter=command_counter)

        end = datetime.now()
        self._post_apply_attack(attack_name=name, start_time=start, end_time=end, post_wait_time=5)

    def _ddos_attack(self, ddos_agent_path='DDosAgent.py', timeout=60, num_process=10, target='192.168.0.11'):
        name = AttackerBase.NAME_ATTACK_DDOS
        log_file = os.path.join(self.log_path, f'log-{name}.txt')
        start = datetime.now()

        _do_ddos_attack(log_dir=self.log_path, log_file=log_file, ddos_agent_path=ddos_agent_path, timeout=timeout,
                        num_process=num_process, target=target)

        end = datetime.now()
        start = start + timedelta(seconds=5)
        self._post_apply_attack(attack_name=name, start_time=start, end_time=end, post_wait_time=5)

    def _post_apply_attack(self, attack_name, start_time, end_time, post_wait_time):
        self.attack_history.info(
            "{},{},{},{},{},{},{},{}".format(
                self.attack_list[attack_name]
                , start_time.timestamp(), end_time.timestamp(), start_time, end_time, self.MAC, self.IP,
                attack_name
            )
        )
        self.report(f'applied {attack_name} attack successfully.')
        self.report(f'waiting {post_wait_time} seconds to cooldown attack.')
        sleep(post_wait_time)
