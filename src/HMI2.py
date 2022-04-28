import logging
import os
import sys

from ics_sim.Device import HMI
from Configs import TAG, Controllers


class HMI2(HMI):
    def __init__(self):
        super().__init__('HMI2', TAG.TAG_LIST, Controllers.PLCs)

    def _display(self):
        menu_line = '{}) To change the {} press {} \n'

        menu = '\n'

        menu += self.__get_menu_line(1, 'empty level of tank')
        menu += self.__get_menu_line(2, 'full level of tank')
        menu += self.__get_menu_line(3, 'full level of bottle')
        menu += self.__get_menu_line(4, 'status of tank Input valve')
        menu += self.__get_menu_line(5, 'status of tank output valve')
        menu += self.__get_menu_line(6, 'status of conveyor belt engine')
        self.report(menu)

    def __get_menu_line(self, number, text):
        return '{} To change the {} press {} \n'.format(
            self._make_text(str(number)+')', self.COLOR_BLUE),
            self._make_text(text, self.COLOR_GREEN),
            self._make_text(str(number), self.COLOR_BLUE)
        )

    def _operate(self):
        try:
            choice = self.__get_choice()
            input1, input2 = choice
            if input1 == 1:
                self._send(TAG.TAG_TANK_LEVEL_MIN, input2)

            elif input1 == 2:
                self._send(TAG.TAG_TANK_LEVEL_MAX, input2)

            elif input1 == 3:
                self._send(TAG.TAG_BOTTLE_LEVEL_MAX, input2)

            elif input1 == 4:
                self._send(TAG.TAG_TANK_INPUT_VALVE_MODE, input2)

            elif input1 == 5:
                self._send(TAG.TAG_TANK_OUTPUT_VALVE_MODE, input2)

            elif input1 == 6:
                self._send(TAG.TAG_CONVEYOR_BELT_ENGINE_MODE, input2)

        except ValueError as e:
            self.report(e.__str__())
        except Exception as e:
            self.report('The input is invalid' + e.__str__())

        input('press inter to continue ...')

    def __get_choice(self):
        input1 = int(input('your choice (1 to 6): '))
        if input1 < 1 or input1 > 6:
            raise ValueError('just integer values between 1 and 6 are acceptable')

        if input1 <= 3:
            input2 = float(input('Specify set point (positive real value): '))
            if input2 < 0:
                raise ValueError('Negative numbers are not acceptable.')
        else:
            sub_menu = '\n'
            sub_menu += "1) Send command for manually off\n"
            sub_menu += "2) Send command for manually on\n"
            sub_menu += "3) Send command for auto operation\n"
            self.report(sub_menu)
            input2 = int(input('Command (1 to 3): '))
            if input2 < 1 or input2 > 3:
                raise ValueError('Just 1, 2, and 3 are acceptable for command')

        return input1, input2


if __name__ == '__main__':
    hmi2 = HMI2()
    hmi2.start()