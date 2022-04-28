import os
import subprocess
import sys
from time import sleep

from ics_sim.Device import Runnable


class Attacker(Runnable):
    def __init__(self):
        Runnable.__init__(self, 'Attacker', 100)

    def _before_start(self):
        sys.stdin = os.fdopen(self._std)
        pass

    def _logic(self):
        os.system('clear')
        menu = '\n'
        menu += '1) To apply Scan Attack with ettercap\n'
        menu += '2) To apply Scan Attack with ping \n'
        menu += '3) To apply Scan Attack with Nmap \n'
        menu += '4) To apply MitM attack \n'
        menu += '5) To apply Dos Attack \n'
        menu += '6) To apply TEMP attack\n'
        self.report(menu)

        try:
            input1 = int(input('your choice (1 to 6): '))
            if input1 < 1 or input1 > 6:
                raise ValueError('just integer values between 1 and 6 are acceptable')

            command = './attacks/attack{}.sh'.format(input1)
            if input1 ==1:
                command = './attacks/scan/scan_ettercap.sh'
            elif input1 == 2:
                command = './attacks/scan/scan_ping.sh'
            elif input1 == 3:
                command = './attacks/scan/scan_nmap.sh'
            elif input1 == 4:
                command = './attacks/mitm/mitm.sh'
            elif input1 == 5:
                command = './attacks/ddos/ddos.sh'

            self.report('running ' + command)
            subprocess.run(command)

        except ValueError as e:
            self.report(e.__str__())

        except Exception as e:
            self.report('The input is invalid' + e.__str__())

        input('press inter to continue ...')


if __name__ == '__main__':
    attacker = Attacker()
    attacker.start()


