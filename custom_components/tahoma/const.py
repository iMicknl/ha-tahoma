"""Constants for the TaHoma integration."""
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR
from homeassistant.components.climate import DOMAIN as CLIMATE
from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.light import DOMAIN as LIGHT
from homeassistant.components.lock import DOMAIN as LOCK
from homeassistant.components.scene import DOMAIN as SCENE
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.components.switch import DOMAIN as SWITCH

DOMAIN = "tahoma"

SUPPORTED_PLATFORMS = [
    BINARY_SENSOR,
    CLIMATE,
    COVER,
    LIGHT,
    LOCK,
    SCENE,
    SENSOR,
    SWITCH,
]

# Used to map the Somfy widget and ui_class to the Home Assistant platform
TAHOMA_TYPES = {
    "AdjustableSlatsRollerShutter": COVER,
    "AirFlowSensor": BINARY_SENSOR,  # widgetName, uiClass is AirSensor (sensor)
    "AirSensor": SENSOR,
    "Awning": COVER,
    "CarButtonSensor": BINARY_SENSOR,
    "ConsumptionSensor": SENSOR,
    "ContactSensor": BINARY_SENSOR,
    "Curtain": COVER,
    "DoorLock": LOCK,
    "ElectricitySensor": SENSOR,
    "ExteriorHeatingSystem": CLIMATE,
    "ExteriorScreen": COVER,
    "ExteriorVenetianBlind": COVER,
    "GarageDoor": COVER,
    "GasSensor": SENSOR,
    "Gate": COVER,
    "Generic": COVER,
    "GenericSensor": SENSOR,
    "HeatingSystem": CLIMATE,
    "HumiditySensor": SENSOR,
    "Light": LIGHT,
    "LightSensor": SENSOR,
    "MotionSensor": BINARY_SENSOR,
    "OccupancySensor": BINARY_SENSOR,
    "OnOff": SWITCH,
    "Pergola": COVER,
    "RainSensor": BINARY_SENSOR,
    "RollerShutter": COVER,
    "Screen": COVER,
    "Shutter": COVER,
    "Siren": SWITCH,
    "SirenStatus": BINARY_SENSOR,  # widgetName, uiClass is Siren (switch)
    "SmokeSensor": BINARY_SENSOR,
    "SunIntensitySensor": SENSOR,
    "SunSensor": SENSOR,
    "SwimmingPool": SWITCH,
    "SwingingShutter": COVER,
    "TemperatureSensor": SENSOR,
    "ThermalEnergySensor": SENSOR,
    "VenetianBlind": COVER,
    "WaterDetectionSensor": BINARY_SENSOR,  # widgetName, uiClass is HumiditySensor (sensor)
    "WaterSensor": SENSOR,
    "WeatherSensor": SENSOR,
    "WindSensor": SENSOR,
    "Window": COVER,
    "WindowHandle": BINARY_SENSOR,
}

CORE_ON_OFF_STATE = "core:OnOffState"

COMMAND_OFF = "off"
COMMAND_ON = "on"
