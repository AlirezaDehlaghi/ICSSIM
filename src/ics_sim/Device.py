import multiprocessing
import os
import sys
import threading
import time
import random
from abc import ABC, abstractmethod
from datetime import datetime

from ics_sim.protocol import ProtocolFactory
from ics_sim.configs import SpeedConfig
from ics_sim.helper import current_milli_time, validate_type, current_milli_cycle_time
from ics_sim.connectors import ConnectorFactory

from multiprocessing import Process
import logging


class Physics(ABC):
    @abstractmethod
    def __init__(self, connection):
        self._connector = ConnectorFactory.build(connection)
        pass

    def _set(self, tag, value):
        return self._connector.set(tag, value)

    def _get(self, tag):
        return self._connector.get(tag)


class SensorConnector(Physics):
    def __init__(self, connection):
        super().__init__(connection)
        self._sensors = {}

    def add_sensor(self, tag, fault):
        self._sensors[tag] = fault

    def read(self, tag):
        if tag in self._sensors.keys():
            value = self._get(tag)
            value += random.uniform(value, -1 * value) * self._sensors[tag]
            return value
        else:
            raise LookupError()


class ActuatorConnector(Physics):
    def __init__(self, connection):
        super().__init__(connection)
        self._actuators = list()

    def add_actuator(self, tag):
        self._actuators.append(tag)

    def write(self, tag, value):
        if tag in self._actuators:
            self._set(tag, value)
        else:
            raise LookupError()


class Runnable(ABC):
    COLOR_RED = '\033[91m'
    COLOR_GREEN = '\033[92m'
    COLOR_BLUE = '\033[94m'
    COLOR_CYAN = '\033[96m'
    COLOR_YELLOW = '\033[93m'
    COLOR_BOLD = '\033[1m'
    COLOR_PURPLE = '\033[35m'

    def __init__(self, name, loop):
        validate_type(name, 'name', str)
        validate_type(loop, 'loop cycle', int)

        self.__name = name
        self.__loop_cycle = loop



        # self.__loop_process = Process(target=self.do_loop, args=())
        self.stop_event = threading.Event()
        self.__loop_process = threading.Thread(target=self.do_loop, args=(self.stop_event,))
        self._last_loop_time = 0
        self._current_loop_time = 0
        self._start_time = 0
        self._last_logic_start = 0
        self._last_logic_end = 0
        self._initialize_logger()
        self.__clear_scr = False
        self._std = sys.stdin.fileno()

        self.report("Created", logging.INFO)

    def _initialize_logger(self):
        self._logger = self.setup_logger(
            "logs-" + self.name(),
            logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        )

    def _set_clear_scr(self, value):
        self.__clear_scr = value

    def _set_logger_level(self, level=logging.DEBUG):
        self._logger.setLevel(level)

    @staticmethod
    def setup_logger(name, format_str, level=logging.INFO, file_dir ="./logs", file_ext =".log", write_mode="w"):
        """To setup as many loggers as you want"""

        """
        logging.basicConfig(filename="./logs/log-" + self.__name +".log",
                            format='[%(levelname)s] [%(asctime)s] %(message)s ',
                            filemode='w')
                            """
        """To setup as many loggers as you want"""
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        file_path = os.path.join(file_dir,name) + file_ext
        handler = logging.FileHandler(file_path, mode=write_mode)
        handler.setFormatter(format_str)

        # Let us Create an object
        logger = logging.getLogger(name)

        # Now we are going to Set the threshold of logger to DEBUG
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def name(self):
        return self.__name

    def start(self):
        self.__loop_process.start()

    def stop(self):
        self._before_stop()
        self.stop_event.set()
        #self.__loop_process.terminate()
        self._after_stop()
        self.report("stopped", logging.INFO)

    def _after_stop(self):
        pass

    def _before_stop(self):
        pass

    def do_loop(self, stop_event):
        try:
            self.report("started", logging.INFO)
            self._before_start()

            self._start_time = self._current_loop_time = current_milli_cycle_time(self.__loop_cycle)
            while not stop_event.is_set():

                self._last_loop_time = self._current_loop_time
                wait = self._last_loop_time + self.__loop_cycle - current_milli_time()

                if wait > 0:
                    time.sleep(wait / 1000)


                self._current_loop_time = current_milli_cycle_time(self.__loop_cycle)
                self._last_logic_start = current_milli_time()

                self._pre_logic_update()
                self._logic()
                self._last_logic_end = current_milli_time()
                self._post_logic_update()
        except Exception as e:
            self.report(e.__str__(), logging.fatal)
            raise e


        except Exception as e:
            self.report(e.__str__(), logging.fatal)
            raise e

    def _before_start(self):
        sys.stdin = os.fdopen(self._std)

    @abstractmethod
    def _logic(self):
        pass

    def _post_logic_update(self):
        pass

    def _pre_logic_update(self):
        if self.__clear_scr:
            os.system('clear')

    def get_loop_latency(self):
        return self._last_logic_start - self._last_loop_time - self.__loop_cycle

    def get_alive_time(self):
        return self._current_loop_time - self._start_time

    def get_logic_execution_time(self):
        return self._last_logic_end - self._last_logic_start 

    def report(self, msg, level=logging.NOTSET):
        name_msg = "[{}] {}".format(self.name(), msg)

        if level == logging.NOTSET:
            self.__show_console(msg)

        elif level == logging.DEBUG:
            self._logger.debug(name_msg)
            self.__show_console(self._make_text("[DEBUG] " + msg, self.COLOR_CYAN))

        elif level == logging.INFO:
            self._logger.info(name_msg)
            self.__show_console(self._make_text("[INFO] " + msg, self.COLOR_GREEN))

        elif level == logging.WARNING or level == logging.WARN:
            self._logger.warning(name_msg)
            self.__show_console(self._make_text("[WARNING] " + msg, self.COLOR_YELLOW))

        elif level == logging.ERROR:
            self._logger.error(name_msg)
            self.__show_console(self._make_text("[ERROR] " + msg, self.COLOR_RED))

        elif level == logging.FATAL or level == logging.CRITICAL:
            self._logger.fatal(name_msg)
            self.__show_console(self._make_text("[FATAL] " + msg, self.COLOR_RED))

    def __show_console(self, msg):
        timestamp = self._make_text( datetime.now().strftime("%H:%M:%S"), self.COLOR_PURPLE)
        name = self._make_text(self.name(), self.COLOR_CYAN)
        print('[{} - {}]\t{}'.format(name, timestamp, msg), flush=True)

    @staticmethod
    def _make_text(msg, color):
        return color + msg + '\033[0m'

class HIL(Runnable, Physics, ABC):
    @abstractmethod
    def __init__(self, name, connection, loop=SpeedConfig.PROCESS_PERIOD):
        Runnable.__init__(self, name, loop)
        Physics.__init__(self, connection)


class DcsComponent(Runnable):
    def __init__(self, name, tags, plcs, loop):
        Runnable.__init__(self, name,  loop)
        self.plcs = plcs
        self.tags = tags
        self.clients = {}
        self.__init_clients()

    def __init_clients(self):
        for plc_id in self.plcs:
            plc = self.plcs[plc_id]
            self.clients[plc_id] = (ProtocolFactory.create_client(plc['protocol'], plc['ip'], plc['port']))

    def _send(self, tag, value):
        tag_id = self.tags[tag]['id']
        plc_id = self.tags[tag]['plc']
        self.clients[plc_id].send(tag_id, value)

    def _receive(self, tag):

        tag_id = self.tags[tag]['id']
        plc_id = self.tags[tag]['plc']

        return self.clients[plc_id].receive(tag_id)

    def _is_input_tag(self, tag):
        return self.tags[tag]['type'] == 'input'

    def _is_output_tag(self, tag):
        return self.tags[tag]['type'] == 'output'

    def _get_tag_id(self, tag):
        return self.tags[tag]['id']

    def _get_tag_fault(self, tag):
        return self.tags[tag]['fault']


class PLC(DcsComponent):
    @abstractmethod
    def __init__(self,
                 plc_id,
                 sensor_connector,
                 actuator_connector,
                 tags,
                 plcs,
                 loop=SpeedConfig.DEFAULT_PLC_PERIOD_MS):

        name = plcs[plc_id]['name']
        DcsComponent.__init__(self, name, tags, plcs, loop)
        self._sensor_connector = sensor_connector
        self._actuator_connector = actuator_connector

        self.id = plc_id
        self.ip = plcs[plc_id]['ip']
        self.port = plcs[plc_id]['port']
        self.protocol = plcs[plc_id]['protocol']

        self.__init_sensors()
        self.__init_actuators()

        self.server = ProtocolFactory.create_server(self.protocol, self.ip, self.port)
        self.report('creating the server on IP = {}:{}'.format(self.ip, self.port), logging.INFO)

        self._snapshot_recorder = self.setup_logger("snapshots_" + self.name(), logging.Formatter('%(message)s'), file_ext=".csv")
        self.__record_variables = False;

    def set_record_variables(self, value):
        self.__record_variables = value


    def _post_logic_update(self):
        DcsComponent._post_logic_update(self)
        self._store_received_values()
        if self.__record_variables:
            self._record_variables()

    def _store_received_values(self):
        for tag_name, tag_data in self.tags.items():
            if not self._is_local_tag(tag_name):
                continue

            if tag_data['type'] == 'output':
                self._set(tag_name, self.server.get(tag_data['id']))
            elif tag_data['type'] == 'input':
                self.server.set(tag_data['id'], self._get(tag_name))

    def _record_variables(self, header=False):
        snapshot = ""

        if header:
            snapshot += "time, current_loop, loop_latency, logic_execution_time, "
        else:
            snapshot += "{}, {}, {}, {}, ".format(
                datetime.now(),
                self._current_loop_time,
                self.get_loop_latency(),
                self.get_logic_execution_time()
            )

        for tag_name, tag_data in self.tags.items():
            if not self._is_local_tag(tag_name):
                continue
            if header:
                snapshot += "{}({}), ".format(tag_name, tag_data['id'])
            else:
                snapshot += "{}, ".format(self._get(tag_name))

        self._snapshot_recorder.info(snapshot)

    def __init_sensors(self):
        for tag in self.tags:
            if self._is_input_tag(tag):
                self._sensor_connector.add_sensor(tag, self._get_tag_fault(tag))

    def __init_actuators(self):
        for tag in self.tags:
            if self._is_output_tag(tag):
                self._actuator_connector.add_actuator(tag)

    def _get(self, tag):
        if self._is_local_tag(tag):

            if self._is_input_tag(tag):
                return self._sensor_connector.read(tag)
            else:
                return self.server.get(self._get_tag_id(tag))
        else:
            try:
                return self._receive(tag)
            except Exception as e:
                self.report('receive null value for tag:{}'.format(tag), logging.WARNING)
                return -1

    def _set(self, tag, value):
        if self._is_local_tag(tag):
            self.server.set(self._get_tag_id(tag), value)
            return self._actuator_connector.write(tag, value)
        else:
            self._send(tag, value)


    def _is_local_tag(self, tag):
        return self.tags[tag]['plc'] == self.id

    def _before_start(self):
        self.server.start()
        for tag, value in self.tags.items():
            if self._is_output_tag(tag) and self._is_local_tag(tag):
                self._set(tag, value['default'])
        self._record_variables(True)

    def stop(self):
        self.server.stop()
        DcsComponent.stop(self)

    def _check_manual_input(self, control_tag, actuator_tag):

        mode = self._get(control_tag)

        if mode == 1:
            self._set(actuator_tag, 0)
            return True
        elif mode == 2:
            self._set(actuator_tag, 1)
            return True
        return False


class HMI(DcsComponent):
    def __init__(self, name,  tags, plcs, loop=SpeedConfig.DEFAULT_PLC_PERIOD_MS):
        DcsComponent.__init__(self, name, tags, plcs, loop)

    def _before_start(self):
        DcsComponent._before_start(self)
        self._set_clear_scr(True)

    def _logic(self):
        self._display()
        self._operate()

    def _display(self):
        pass

    def _operate(self):
        pass

























