import logging
from datetime import datetime

from ics_sim.Device import HMI
from Configs import TAG, Controllers


class HMI1(HMI):
    def __init__(self):
        super().__init__('HMI1', TAG.TAG_LIST, Controllers.PLCs, 500)

        self._rows = {}
        self.title_length = 27
        self.msg1_length = 21
        self.msg2_length = 10
        self._border = '-' * (self.title_length + self.msg1_length + self.msg2_length + 4)

        self._border_top = \
            "┌" + "─" * self.title_length + "┬" + "─" * self.msg1_length + "┬" + "─" * self.msg2_length + "┐"
        self._border_mid = \
            "├" + "─" * self.title_length + "┼" + "─" * self.msg1_length + "┼" + "─" * self.msg2_length + "┤"
        self._border_bot = \
            "└" + "─" * self.title_length + "┴" + "─" * self.msg1_length + "┴" + "─" * self.msg2_length + "┘"

        self.cellVerticalLine = "│"

        for tag in self.tags:
            pos = tag.rfind('_')
            tag_name = tag[0:pos]
            if not self._rows.keys().__contains__(tag_name):
                self._rows[tag_name] = {'tag': tag_name.center(self.title_length, ' '), 'msg1': '', 'msg2': ''}

        self._latency = 0

    def _display(self):

        self.__show_table()

    def _operate(self):
        self.__update_massages()

    def __update_massages(self):
        self._latency = 0

        for row in self._rows:
            self._rows[row]['msg1'] = ''
            self._rows[row]['msg2'] = ''

        for tag in self.tags:
            pos = tag.rfind('_')
            row = tag[0:pos]
            attribute = tag[pos + 1:]

            if attribute == 'value' or attribute == 'status':
                self._rows[row]['msg2'] += self.__get_formatted_value(tag)
            elif attribute == 'max':
                self._rows[row]['msg1'] += self.__get_formatted_value(tag)
                self._rows[row]['msg1'] = self._make_text(self._rows[row]['msg1'].center(self.msg1_length, " "), self.COLOR_GREEN)
            else:
                self._rows[row]['msg1'] += self.__get_formatted_value(tag)

        for row in self._rows:
            if self._rows[row]['msg1'] == '':
                self._rows[row]['msg1'] = ''.center(self.msg1_length, ' ')
            if self._rows[row]['msg2'] == '':
                self._rows[row]['msg2'] = ''.center(self.msg1_length, ' ')

    def __get_formatted_value(self, tag):
        timestamp = datetime.now()
        pos = tag.rfind('_')
        tag_name = tag[0:pos]
        tag_attribute = tag[pos + 1:]

        try:
            value = self._receive(tag)
        except Exception as e:
            self.report(e.__str__(), logging.WARNING)
            value = 'NULL'

        if tag_attribute == 'mode':
            if value == 1:
                value = self._make_text('Off manually'.center(self.msg1_length, " "), self.COLOR_YELLOW)
            elif value == 2:
                value = self._make_text('On manually'.center(self.msg1_length, " "), self.COLOR_YELLOW)
            elif value == 3:
                value = self._make_text('Auto'.center(self.msg1_length, " "), self.COLOR_GREEN)
            else:

                value = self._make_text(str(value).center(self.msg1_length, " "), self.COLOR_RED)

        elif tag_attribute == 'status' or self.tags[tag]['id'] == 7:
            if value == 'NULL':
                value = self._make_text(value.center(self.msg2_length, " "), self.COLOR_RED)
            elif value:
                value = self._make_text('>>>'.center(self.msg2_length, " "), self.COLOR_BLUE)
            else:
                value = self._make_text('X'.center(self.msg2_length, " "), self.COLOR_RED)

        elif tag_attribute == 'min':
            value = 'Min:' + str(value) + ' '

        elif tag_attribute == 'max':
            value = 'Max:' + str(value)

        elif value == 'NULL':
            value = self._make_text(value.center(self.msg2_length, " "), self.COLOR_RED)
        else:
            value = self._make_text(str(value).center(self.msg2_length, " "), self.COLOR_CYAN)

        elapsed = datetime.now() - timestamp

        if elapsed.microseconds > self._latency:
            self._latency = elapsed.microseconds
        return value

    def __show_table(self):
        result = " (Latency {}ms)\n".format(self._latency / 1000)

        first = True
        for row in self._rows:
            if first:
                result += self._border_top + "\n"
                first = False
            else:
                result += self._border_mid + "\n"

            result += '│{}│{}│{}│\n'.format(self._rows[row]['tag'], self._rows[row]['msg1'], self._rows[row]['msg2'])

        result += self._border_bot + "\n"

        self.report(result)


if __name__ == '__main__':
    hmi1 = HMI1()
    hmi1.start()
