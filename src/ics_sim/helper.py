import time


def validate_type(variable: str, variable_name: str, variable_type: type):
    if type(variable) is not variable_type:
        raise TypeError('{0} type is not valid for {1}.'.format(type(variable), variable_name))
    elif not variable_type:
        raise ValueError('Empty {0} is not valid.'.format(variable_name))


def current_milli_time():
    return round(time.time() * 1000)


def current_milli_cycle_time(cycle):
    return round(time.time() * 1000 / cycle) * cycle


def debug(msg):
    print('DEBUG: ', msg)


def error(msg):
    print('ERROR: ', msg)
