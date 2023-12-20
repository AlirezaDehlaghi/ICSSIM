import os
from src.AttackerBase import AttackerBase


class Attacker(AttackerBase):
    def __init__(self):
        AttackerBase.__init__(self, 'attacker')

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
        for attack in self.attack_list.keys():
            i += 1
            menu += self.__get_menu_line('{} To apply the {} attack press {} \n', i , attack)
        self.report(menu)

        try:
            attack_name = int(input('your choice (1 to {}): '.format(self.attack_cnt)))

            if int(attack_name) == 0:
                os.system('clear')
                return

            attack_short_name = attack_name

            if 0 < attack_name <= self.attack_cnt:
                attack_name = list(self.attack_list.keys())[attack_name-1]
                attack_short_name = self.attack_list[attack_name]

            self._apply_attack(attack_short_name, attack_name)

        except ValueError as e:
            self.report(e.__str__())

        except Exception as e:
            self.report('The input is invalid ' + e.__str__())

        input('press inter to continue ...')


if __name__ == '__main__':
    attacker = Attacker()
    attacker.start()
