import logging
import os
import random
import subprocess
from datetime import datetime, timedelta
from time import sleep

from AttackerBase import AttackerBase


class AttackerMachine(AttackerBase):
    def __init__(self):
        AttackerBase.__init__(self, 'attacker_machine')

    def _before_start(self):
        AttackerBase._before_start(self)

        self.__attack_scenario = []
        self.__attack_scenario += ['scan-ettercap'] * 0  # this should be 0, cannot automate
        self.__attack_scenario += ['scan-ping'] * 0
        self.__attack_scenario += ['scan-nmap'] * 16
        self.__attack_scenario += ['scan-scapy'] * 21
        self.__attack_scenario += ['mitm-scapy'] * 14
        self.__attack_scenario += ['mitm-ettercap'] * 0
        self.__attack_scenario += ['ddos'] * 7
        self.__attack_scenario += ['replay-scapy'] * 7

        random.shuffle(self.__attack_scenario)


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
                self._apply_attack(attack_name)

                if not self.__status_board.keys().__contains__(attack_name):
                    self.__status_board[attack_name] = 0
                self.__status_board[attack_name] += 1

                for attack in self.__status_board.keys():
                    text = '{}: applied {} times'.format(attack, self.__status_board[attack])
                    self.report(self._make_text(text, self.COLOR_GREEN))

            except ValueError as e:
                self.report(e.__str__())

            except Exception as e:
                self.report('The input is invalid ' + e.__str__())

        input('press inter to continue ...')


if __name__ == '__main__':
    attackerMachine = AttackerMachine()
    attackerMachine.start()
