class SimulationConfig:
    # Constants
    EXECUTION_MODE_LOCAL = 'local'
    EXECUTION_MODE_DOCKER = 'docker'
    EXECUTION_MODE_GNS3 = 'gns3'

    # configurable
    EXECUTION_MODE = EXECUTION_MODE_DOCKER



class PHYSICS:
    TANK_LEVEL_CAPACITY = 3     # Liter
    TANK_MAX_LEVEL = 10
    TANK_INPUT_FLOW_RATE = 0.0002  # Liter/mil-second
    TANK_OUTPUT_FLOW_RATE = 0.0001  # Liter/mil-second

    BOTTLE_LEVEL_CAPACITY = 0.75   # Liter
    BOTTLE_MAX_LEVEL = 2
    BOTTLE_DISTANCE = 20  # Centimeter

    CONVEYOR_BELT_SPEED = 0.005  # Centimeter/mil-second


class TAG:
    TAG_TANK_INPUT_VALVE_STATUS = 'tank_input_valve_status'
    TAG_TANK_INPUT_VALVE_MODE = 'tank_input_valve_mode'

    TAG_TANK_LEVEL_VALUE = 'tank_level_value'
    TAG_TANK_LEVEL_MAX = 'tank_level_max'
    TAG_TANK_LEVEL_MIN = 'tank_level_min'

    TAG_TANK_OUTPUT_VALVE_STATUS = 'tank_output_valve_status'
    TAG_TANK_OUTPUT_VALVE_MODE = 'tank_output_valve_mode'

    TAG_TANK_OUTPUT_FLOW_VALUE = 'tank_output_flow_value'

    TAG_CONVEYOR_BELT_ENGINE_STATUS= 'conveyor_belt_engine_status'
    TAG_CONVEYOR_BELT_ENGINE_MODE = 'conveyor_belt_engine_mode'

    TAG_BOTTLE_LEVEL_VALUE = 'bottle_level_value'
    TAG_BOTTLE_LEVEL_MAX = 'bottle_level_max'

    TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE = 'bottle_distance_to_filler_value'

    TAG_LIST = {
        # tag_name (tag_id, PLC number, input/output, fault (just for inputs)
        TAG_TANK_INPUT_VALVE_STATUS:             {'id': 0, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 1},
        TAG_TANK_INPUT_VALVE_MODE:              {'id': 1, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 3},

        TAG_TANK_LEVEL_VALUE:                   {'id': 2, 'plc': 1, 'type': 'input',  'fault': 0.0, 'default': 5.8},
        TAG_TANK_LEVEL_MIN:                     {'id': 3, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 3},
        TAG_TANK_LEVEL_MAX:                     {'id': 4, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 7},


        TAG_TANK_OUTPUT_VALVE_STATUS:            {'id': 5, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 0},
        TAG_TANK_OUTPUT_VALVE_MODE:             {'id': 6, 'plc': 1, 'type': 'output', 'fault': 0.0, 'default': 3},

        TAG_TANK_OUTPUT_FLOW_VALUE:             {'id': 7, 'plc': 1, 'type': 'input',  'fault': 0.0, 'default': 0},

        TAG_CONVEYOR_BELT_ENGINE_STATUS:         {'id': 8, 'plc': 2, 'type': 'output', 'fault': 0.0, 'default': 0},
        TAG_CONVEYOR_BELT_ENGINE_MODE:          {'id': 9, 'plc': 2, 'type': 'output', 'fault': 0.0, 'default': 3},

        TAG_BOTTLE_LEVEL_VALUE:                 {'id': 10, 'plc': 2, 'type': 'input', 'fault': 0.0, 'default': 0},
        TAG_BOTTLE_LEVEL_MAX:                   {'id': 11, 'plc': 2, 'type': 'output', 'fault': 0.0, 'default': 1.8},

        TAG_BOTTLE_DISTANCE_TO_FILLER_VALUE:    {'id': 12, 'plc': 2, 'type': 'input', 'fault': 0.0, 'default': 0},
    }


class Controllers:
    PLC_CONFIG = {
        SimulationConfig.EXECUTION_MODE_DOCKER: {
            1: {
                'name': 'PLC1',
                'ip': '192.168.0.11',
                'port': 502,
                'protocol': 'ModbusWriteRequest-TCP'
             },
            2: {
                'name': 'PLC2',
                'ip': '192.168.0.12',
                'port': 502,
                'protocol': 'ModbusWriteRequest-TCP'
             },
        },
        SimulationConfig.EXECUTION_MODE_GNS3: {
            1: {
                'name': 'PLC1',
                'ip': '192.168.0.11',
                'port': 502,
                'protocol': 'ModbusWriteRequest-TCP'
            },
            2: {
                'name': 'PLC2',
                'ip': '192.168.0.12',
                'port': 502,
                'protocol': 'ModbusWriteRequest-TCP'
            },
        },
        SimulationConfig.EXECUTION_MODE_LOCAL: {
            1: {
                'name': 'PLC1',
                'ip': '127.0.0.1',
                'port': 5502,
                'protocol': 'ModbusWriteRequest-TCP'
             },
            2: {
                'name': 'PLC2',
                'ip': '127.0.0.1',
                'port': 5503,
                'protocol': 'ModbusWriteRequest-TCP'
             },
        }
    }

    PLCs = PLC_CONFIG[SimulationConfig.EXECUTION_MODE]


class Connection:
    SQLITE_CONNECTION = {
        'type': 'sqlite',
        'path': 'storage/PhysicalSimulation1.sqlite',
        'name': 'fp_table',
    }
    MEMCACHE_DOCKER_CONNECTION = {
        'type': 'memcache',
        'path': '192.168.1.31:11211',
        'name': 'fp_table',
    }
    MEMCACHE_LOCAL_CONNECTION = {
        'type': 'memcache',
        'path': '127.0.0.1:11211',
        'name': 'fp_table',
    }
    File_CONNECTION = {
        'type': 'file',
        'path': 'storage/sensors_actuators.json',
        'name': 'fake_name',
    }

    CONNECTION_CONFIG = {
        SimulationConfig.EXECUTION_MODE_GNS3: MEMCACHE_DOCKER_CONNECTION,
        SimulationConfig.EXECUTION_MODE_DOCKER: SQLITE_CONNECTION, #todo : return back to sqlite connection
        SimulationConfig.EXECUTION_MODE_LOCAL: SQLITE_CONNECTION
    }
    CONNECTION = CONNECTION_CONFIG[SimulationConfig.EXECUTION_MODE]

