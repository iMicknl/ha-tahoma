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

# Used to map the Somfy widget and uiClass to the Home Assistant platform
TAHOMA_TYPES = {
    "SirenStatus": BINARY_SENSOR,  # widgetName, uiClass is Siren (switch)
    "Light": LIGHT,
    "ExteriorScreen": COVER,
    "Pergola": COVER,
    "RollerShutter": COVER,
    "Window": COVER,
    "HeatingSystem": CLIMATE,
    "TemperatureSensor": SENSOR,
    "LightSensor": SENSOR,
    "DoorLock": LOCK,
    "OnOff": SWITCH,
    "AirFlowSensor": BINARY_SENSOR,  # widgetName, uiClass is AirSensor (sensor)
    "WaterDetectionSensor": BINARY_SENSOR,  # widgetName, uiClass is HumiditySensor (sensor)
    "HumiditySensor": SENSOR,
    "GarageDoor": COVER,
    "CarButtonSensor": BINARY_SENSOR,
    "ContactSensor": BINARY_SENSOR,
    "RainSensor": BINARY_SENSOR,
    "SmokeSensor": BINARY_SENSOR,
    "OccupancySensor": BINARY_SENSOR,
    "MotionSensor": BINARY_SENSOR,
    "WindowHandle": BINARY_SENSOR,
    "ExteriorVenetianBlind": COVER,
    "Awning": COVER,
    "Gate": COVER,
    "Curtain": COVER,
    "Generic": COVER,
    "SwingingShutter": COVER,
    "Screen": COVER,
    "ElectricitySensor": SENSOR,
    "AirSensor": SENSOR,
    "Siren": SWITCH,
    "WindSensor": SENSOR,
    "SunSensor": SENSOR,
    "SwimmingPool": SWITCH,
}

CORE_ON_OFF_STATE = "core:OnOffState"

COMMAND_OFF = "off"
COMMAND_ON = "on"
