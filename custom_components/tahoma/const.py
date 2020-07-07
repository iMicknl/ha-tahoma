"""Constants for the TaHoma integration."""

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
    "AirFlowSensor": "binary_sensor",  # widgetName, uiClass is AirSensor (sensor)
    "WaterDetectionSensor": "binary_sensor",  # widgetName, uiClass is HumiditySensor (sensor)
    "HumiditySensor": "sensor",
    "GarageDoor": "cover",
    "CarButtonSensor": "binary_sensor",
    "ContactSensor": "binary_sensor",
    "RainSensor": "binary_sensor",
    "SmokeSensor": "binary_sensor",
    "OccupancySensor": "binary_sensor",
    "MotionSensor": "binary_sensor",
    "WindowHandle": "binary_sensor",
    "ExteriorVenetianBlind": "cover",
    "Awning": "cover",
    "Gate": "cover",
    "Curtain": "cover",
    "Generic": "cover",
    "SwingingShutter": "cover",
    "ElectricitySensor": "sensor",
    "AirSensor": "sensor",
    "Siren": "switch",
    "WindSensor": "sensor",
    "SunSensor": "sensor",
}

CORE_ON_OFF_STATE = "core:OnOffState"

COMMAND_OFF = "off"
COMMAND_ON = "on"

ICON_WEATHER_WINDY = "mdi:weather-windy"
