"""Constants for the TaHoma integration."""

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_OCCUPANCY,
    DEVICE_CLASS_OPENING,
    DEVICE_CLASS_SMOKE,
)
from homeassistant.components.cover import (
    DEVICE_CLASS_AWNING,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_CURTAIN,
    DEVICE_CLASS_GARAGE,
    DEVICE_CLASS_GATE,
    DEVICE_CLASS_SHUTTER,
    DEVICE_CLASS_WINDOW,
)
from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
)

DOMAIN = "tahoma"

# Used to map the Somfy uiClass to the Home Assistant platform
TAHOMA_TYPES = {
    "Light": "light",
    "ExteriorScreen": "cover",
    "Pergola": "cover",
    "RollerShutter": "cover",
    "Window": "cover",
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
    "WindowHandle": "binary_sensor",
    "ExteriorVenetianBlind": "cover",
    "Awning": "cover",
    "Gate": "cover",
    "Curtain": "cover",
    "Generic": "cover",
    "SwingingShutter": "cover",
    "ElectricitySensor": "sensor",
    "AirSensor": "sensor",
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
    "Gate": DEVICE_CLASS_GATE,
    "Curtain": DEVICE_CLASS_CURTAIN,
    "SwingingShutter": DEVICE_CLASS_SHUTTER,
}


# Used to map the Somfy widget or uiClass to the Home Assistant device classes
TAHOMA_BINARY_SENSOR_DEVICE_CLASSES = {
    "SmokeSensor": DEVICE_CLASS_SMOKE,
    "OccupancySensor": DEVICE_CLASS_OCCUPANCY,
    "ContactSensor": DEVICE_CLASS_OPENING,
    "WindowHandle": DEVICE_CLASS_OPENING,
}

# Used to map the Somfy widget or uiClass to the Home Assistant device classes
TAHOMA_SENSOR_DEVICE_CLASSES = {
    "TemperatureSensor": DEVICE_CLASS_TEMPERATURE,
    "HumiditySensor": DEVICE_CLASS_HUMIDITY,
    "LightSensor": DEVICE_CLASS_ILLUMINANCE,
    "ElectricitySensor": DEVICE_CLASS_POWER,
    "AirSensor": "carbon dioxide",
}

# TaHoma Attributes
ATTR_MEM_POS = "memorized_position"
ATTR_RSSI_LEVEL = "rssi_level"
ATTR_LOCK_START_TS = "lock_start_ts"
ATTR_LOCK_END_TS = "lock_end_ts"
ATTR_LOCK_LEVEL = "lock_level"
ATTR_LOCK_ORIG = "lock_originator"

# TaHoma internal device states
CORE_RSSI_LEVEL_STATE = "core:RSSILevelState"
CORE_STATUS_STATE = "core:StatusState"
CORE_CLOSURE_STATE = "core:ClosureState"
CORE_TARGET_CLOSURE_STATE = "core:TargetClosureState"
CORE_DEPLOYMENT_STATE = "core:DeploymentState"
CORE_SLATS_ORIENTATION_STATE = "core:SlatsOrientationState"
CORE_PRIORITY_LOCK_TIMER_STATE = "core:PriorityLockTimerState"
CORE_SENSOR_DEFECT_STATE = "core:SensorDefectState"
CORE_CONTACT_STATE = "core:ContactState"
CORE_OCCUPANCY_STATE = "core:OccupancyState"
CORE_SMOKE_STATE = "core:SmokeState"
CORE_TEMPERATURE_STATE = "core:TemperatureState"
CORE_RELATIVE_HUMIDITY_STATE = "core:RelativeHumidityState"
CORE_MEMORIZED_1_POSITION_STATE = "core:Memorized1PositionState"
CORE_PEDESTRIAN_POSITION_STATE = "core:PedestrianPositionState"
CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE = "core:ElectricEnergyConsumptionState"
CORE_ELECTRIC_POWER_CONSUMPTION_STATE = "core:ElectricPowerConsumptionState"
CORE_CO2_CONCENTRATION_STATE = "core:CO2ConcentrationState"

# Light core states
CORE_LUMINANCE_STATE = "core:LuminanceState"
CORE_RED_COLOR_INTENSITY_STATE = "core:RedColorIntensityState"
CORE_GREEN_COLOR_INTENSITY_STATE = "core:GreenColorIntensityState"
CORE_BLUE_COLOR_INTENSITY_STATE = "core:BlueColorIntensityState"

IO_PRIORITY_LOCK_LEVEL_STATE = "io:PriorityLockLevelState"
IO_PRIORITY_LOCK_ORIGINATOR_STATE = "io:PriorityLockOriginatorState"

# Commands
COMMAND_SET_CLOSURE = "setClosure"
COMMAND_SET_POSITION = "setPosition"
COMMAND_SET_ORIENTATION = "setOrientation"
COMMAND_SET_PEDESTRIAN_POSITION = "setPedestrianPosition"
