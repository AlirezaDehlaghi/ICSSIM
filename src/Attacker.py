import os
from AttackerBase import AttackerBase


class Attacker(AttackerBase):
    def __init__(self):
        AttackerBase.__init__(self, 'attacker')

    def __get_menu_line(self, template, number, text):
        return template.format(
            self._make_text(str(number)+')', self.COLOR_BLUE),
            self._make_text(text, self.COLOR_YELLOW),
            self._make_text(str(number), self.COLOR_BLUE)
        )

    def __create_menu(self):
        menu = "\n" + self.__get_menu_line('{} to {} press {} \n', 0, 'clear')
        i = 0
        for attack in self.attack_list.keys():
            i += 1
            menu += self.__get_menu_line('{} To apply the {} attack press {} \n', i, attack)

        return menu

    def _logic(self):
        self.report(self.__create_menu())
        attack_cnt = len(self.attack_list)

        try:
            attack_name = int(input('your choice (1 to {}): '.format(attack_cnt)))

            if int(attack_name) == 0:
                os.system('clear')
                return

            if 0 < attack_name <= attack_cnt:
                attack_name = list(self.attack_list.keys())[attack_name-1]

            self._apply_attack(attack_name)

        except ValueError as e:
            self.report(e.__str__())

        except Exception as e:
            self.report('The input is invalid ' + e.__str__())

        input('press inter to continue ...')


if __name__ == '__main__':
    attacker = Attacker()
    attacker.start()
