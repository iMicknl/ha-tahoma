"""Constants for the TaHoma integration."""
from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_CONTROL_PANEL
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR
from homeassistant.components.climate import DOMAIN as CLIMATE
from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.light import DOMAIN as LIGHT
from homeassistant.components.lock import DOMAIN as LOCK
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.components.switch import DOMAIN as SWITCH
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER

CONF_HUB = "hub"
DOMAIN = "tahoma"

DEFAULT_HUB = "Somfy TaHoma"
SUPPORTED_ENDPOINTS = {
    "Cozytouch": "https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "eedomus": "https://ha101-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Hi Kumo": "https://ha117-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Rexel Energeasy Connect": "https://ha112-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Somfy Connexoon IO": "https://tahomalink.com/enduser-mobile-web/enduserAPI/",
    "Somfy Connexoon RTS": "https://ha201-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Somfy TaHoma": "https://tahomalink.com/enduser-mobile-web/enduserAPI/",
}

HUB_MANUFACTURER = {
    "Cozytouch": "Cozytouch",
    "eedomus": "eedomus",
    "Hi Kumo": "Hitachi",
    "Rexel Energeasy Connect": "Rexel",
    "Somfy Connexoon IO": "Somfy",
    "Somfy Connexoon RTS": "Somfy",
    "Somfy TaHoma": "Somfy",
}

MIN_UPDATE_INTERVAL = 30
DEFAULT_UPDATE_INTERVAL = 30

IGNORED_TAHOMA_DEVICES = [
    "ProtocolGateway",
    "Pod",
]

# Used to map the Somfy widget and ui_class to the Home Assistant platform
TAHOMA_DEVICE_TO_PLATFORM = {
    "AdjustableSlatsRollerShutter": COVER,
    "AirFlowSensor": BINARY_SENSOR,  # widgetName, uiClass is AirSensor (sensor)
    "AirSensor": SENSOR,
    "Alarm": ALARM_CONTROL_PANEL,
    "AtlanticElectricalHeater": CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    "AtlanticPassAPCDHW": CLIMATE,  # widgetName, uiClass is WaterHeatingSystem (not supported)
    "Awning": COVER,
    "CarButtonSensor": BINARY_SENSOR,
    "ConsumptionSensor": SENSOR,
    "ContactSensor": BINARY_SENSOR,
    "Curtain": COVER,
    "DimmerExteriorHeating": CLIMATE,  # widgetName, uiClass is ExteriorHeatingSystem (not supported)
    "DomesticHotWaterProduction": WATER_HEATER,  # widgetName, uiClass is WaterHeatingSystem (not supported)
    "DomesticHotWaterTank": SWITCH,  # widgetName, uiClass is WaterHeatingSystem (not supported)
    "DoorLock": LOCK,
    "ElectricitySensor": SENSOR,
    "ExteriorScreen": COVER,
    "ExteriorVenetianBlind": COVER,
    "GarageDoor": COVER,
    "GasSensor": SENSOR,
    "Gate": COVER,
    "GenericSensor": SENSOR,
    "HeatingSetPoint": CLIMATE,  # widgetName, uiClass is EvoHome (not supported)
    "HitachiDHW": WATER_HEATER,  # widgetName, uiClass is HitachiHeatingSystem (not supported)
    "HitachiAirToWaterHeatingZone": CLIMATE,  # widgetName, uiClass is HitachiHeatingSystem (not supported)
    "HumiditySensor": SENSOR,
    "Light": LIGHT,
    "LightSensor": SENSOR,
    "MotionSensor": BINARY_SENSOR,
    "MyFoxSecurityCamera": COVER,  # widgetName, uiClass is Camera (not supported)
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
    "SomfyThermostat": CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    "StatelessExteriorHeating": CLIMATE,  # widgetName, uiClass is ExteriorHeatingSystem.
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

CONF_UPDATE_INTERVAL = "update_interval"
