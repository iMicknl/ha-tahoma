from homeassistant.components.cover import (
    DEVICE_CLASS_AWNING,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_CURTAIN,
    DEVICE_CLASS_GARAGE,
    DEVICE_CLASS_SHUTTER,
    DEVICE_CLASS_WINDOW,
)

"""Constants for the Tahoma integration."""

DOMAIN = "tahoma"

# Tahoma to Home Assistant mapping
TAHOMA_TYPES = {
    "Light": "light",
    "ExteriorScreen": "cover",
    "Pergola": "cover",
    "RollerShutter": "cover",
    "Window": "cover",
    "RemoteController": "",
    "HeatingSystem": "climate",
    "TemperatureSensor": "sensor",
    "DoorLock": "lock",
    "OnOff": "switch",
    "HumiditySensor": "sensor",
}

## TODO Make sure widgetName has priority over uiClass for specific overrides.
TAHOMA_COVER_DEVICE_CLASSES = {
    "ExteriorScreen": DEVICE_CLASS_BLIND,
    "Pergola": DEVICE_CLASS_AWNING,
    "RollerShutter": DEVICE_CLASS_SHUTTER,
    "Window": DEVICE_CLASS_WINDOW,
}

# Tahoma Attributes
ATTR_MEM_POS = "memorized_position"
ATTR_RSSI_LEVEL = "rssi_level"
ATTR_LOCK_START_TS = "lock_start_ts"
ATTR_LOCK_END_TS = "lock_end_ts"
ATTR_LOCK_LEVEL = "lock_level"
ATTR_LOCK_ORIG = "lock_originator"

# Tahoma internal device states
CORE_RSSI_LEVEL_STATE = "core:RSSILevelState"
CORE_STATUS_STATE = "core:StatusState"
CORE_CLOSURE_STATE = "core:ClosureState"
CORE_DEPLOYMENT_STATE = "core:DeploymentState"
CORE_SLATS_ORIENTATION_STATE = "core:SlatsOrientationState"
CORE_PRIORITY_LOCK_TIMER_STATE = "core:PriorityLockTimerState"
CORE_SENSOR_DEFECT_STATE = "core:SensorDefectState"

IO_PRIORITY_LOCK_LEVEL_STATE = "io:PriorityLockLevelState"
IO_PRIORITY_LOCK_ORIGINATOR_STATE = "io:PriorityLockOriginatorState"

# Commands
COMMAND_SET_CLOSURE = "setClosure"
COMMAND_SET_POSITION = "setPosition"
