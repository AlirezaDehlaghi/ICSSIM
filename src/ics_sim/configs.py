class SpeedConfig:
    # Constants
    SPEED_MODE_FAST = 'fast'
    SPEED_MODE_MEDIUM = 'medium'
    SPEED_MODE_SLOW = 'slow'

    PLC_PERIOD = {
        SPEED_MODE_FAST: 200,
        SPEED_MODE_MEDIUM: 500,
        SPEED_MODE_SLOW: 1000
        }
    PROCESS_PERIOD = {
        SPEED_MODE_FAST: 50,
        SPEED_MODE_MEDIUM: 100,
        SPEED_MODE_SLOW: 200
        }

    # you code configure SPEED_MODE
    SPEED_MODE = SPEED_MODE_FAST

    DEFAULT_PLC_PERIOD_MS = PLC_PERIOD[SPEED_MODE]
    DEFAULT_FP_PERIOD_MS = PROCESS_PERIOD[SPEED_MODE]


