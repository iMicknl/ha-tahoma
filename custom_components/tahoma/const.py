from homeassistant.components.cover import (
    DEVICE_CLASS_AWNING,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_CURTAIN,
    DEVICE_CLASS_GARAGE,
    DEVICE_CLASS_SHUTTER,
    DEVICE_CLASS_WINDOW,
    DEVICE_CLASS_GATE
)

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_SMOKE,
    DEVICE_CLASS_OCCUPANCY,
    DEVICE_CLASS_OPENING
)

"""Constants for the Tahoma integration."""

DOMAIN = "tahoma"

# Used to map the Somfy uiClass to the Home Assistant platform
TAHOMA_TYPES = {
    "Light": "light",
    "ExteriorScreen": "cover",
    "Pergola": "cover",
    "RollerShutter": "cover",
    "Window": "cover",
    "RemoteController": "",
    "HeatingSystem": "climate",
    "TemperatureSensor": "sensor",
    "LightSensor": "sensor",
    "DoorLock": "lock",
    "OnOff": "switch",
    "HumiditySensor": "sensor",
    "GarageDoor": "cover",
    "ContactSensor": "binary_sensor",
    "SmokeSensor": "binary_sensor",
    "OccupancySensor": "binary_sensor",
    "ExteriorVenetianBlind": "cover",
    "Awning": "cover",
    "Gate": "cover"
}

# Used to map the Somfy widget or uiClass to the Home Assistant device classes
TAHOMA_COVER_DEVICE_CLASSES = {
    "Awning": DEVICE_CLASS_AWNING,
    "ExteriorScreen": DEVICE_CLASS_BLIND,
    "Pergola": DEVICE_CLASS_AWNING,
    "RollerShutter": DEVICE_CLASS_SHUTTER,
    "Window": DEVICE_CLASS_WINDOW,
    "Blind": DEVICE_CLASS_BLIND,
    "GarageDoor": DEVICE_CLASS_GARAGE,
    "ExteriorVenetianBlind": DEVICE_CLASS_BLIND,
    "VeluxInteriorBlind": DEVICE_CLASS_BLIND,
    "Gate": DEVICE_CLASS_GATE
}

# Used to map the Somfy widget or uiClass to the Home Assistant device classes
TAHOMA_BINARY_SENSOR_DEVICE_CLASSES = {
    "SmokeSensor": DEVICE_CLASS_SMOKE,
    "OccupancySensor": DEVICE_CLASS_OCCUPANCY,
    "ContactSensor": DEVICE_CLASS_OPENING 
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
CORE_CONTACT_STATE = "core:ContactState"
CORE_OCCUPANCY_STATE = "core:OccupancyState"
CORE_SMOKE_STATE = "core:SmokeState"
CORE_TEMPERATURE_STATE = "core:TemperatureState"
CORE_LUMINANCE_STATE = "core:LuminanceState"
CORE_RELATIVE_HUMIDITY_STATE = "core:RelativeHumidityState"
CORE_MEMORIZED_1_POSITION_STATE = "core:Memorized1PositionState"
CORE_PEDESTRIAN_POSITION_STATE = "core:PedestrianPositionState"

IO_PRIORITY_LOCK_LEVEL_STATE = "io:PriorityLockLevelState"
IO_PRIORITY_LOCK_ORIGINATOR_STATE = "io:PriorityLockOriginatorState"

# Commands
COMMAND_SET_CLOSURE = "setClosure"
COMMAND_SET_POSITION = "setPosition"
COMMAND_SET_ORIENTATION = "setOrientation"
COMMAND_SET_PEDESTRIAN_POSITION = "setPedestrianPosition"