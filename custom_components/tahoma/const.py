"""Constants for the TaHoma integration."""
from dataclasses import dataclass

from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_CONTROL_PANEL
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR
from homeassistant.components.climate import DOMAIN as CLIMATE
from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.light import DOMAIN as LIGHT
from homeassistant.components.lock import DOMAIN as LOCK
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.components.switch import DOMAIN as SWITCH
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER

DOMAIN = "tahoma"

CONF_HUB = "hub"
DEFAULT_HUB = "Somfy (Europe)"


@dataclass
class OverkizHub:
    """Class to describe a hub."""

    endpoint: str
    name: str
    manufacturer: str


SUPPORTED_HUBS = {
    "atlantic_cozytouch": OverkizHub(
        name="Atlantic Cozytouch",
        endpoint="https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/",
        manufacturer="Atlantic",
    ),
    "hi_kumo_asia": OverkizHub(
        name="Hitachi Hi Kumo (Asia)",
        endpoint="https://ha203-1.overkiz.com/enduser-mobile-web/enduserAPI/",
        manufacturer="Hitachi",
    ),
    "hi_kumo_europe": OverkizHub(
        name="Hitachi Hi Kumo (Europe)",
        endpoint="https://ha117-1.overkiz.com/enduser-mobile-web/enduserAPI/",
        manufacturer="Hitachi",
    ),
    "hi_kumo_oceania": OverkizHub(
        name="Hitachi Hi Kumo (Oceania)",
        endpoint="https://ha203-1.overkiz.com/enduser-mobile-web/enduserAPI/",
        manufacturer="Hitachi",
    ),
    "nexity": OverkizHub(
        name="Nexity Eugénie",
        endpoint="https://ha106-1.overkiz.com/enduser-mobile-web/enduserAPI/",
        manufacturer="Nexity",
    ),
    "rexel": OverkizHub(
        name="Rexel Energeasy Connect",
        endpoint="https://ha112-1.overkiz.com/enduser-mobile-web/enduserAPI/",
        manufacturer="Rexel",
    ),
    "somfy_europe": OverkizHub(
        name="Somfy (Europe)",
        endpoint="https://tahomalink.com/enduser-mobile-web/enduserAPI/",  # uses https://ha101-1.overkiz.com
        manufacturer="Somfy",
    ),
    "somfy_america": OverkizHub(
        name="Somfy (North America)",
        endpoint="https://ha401-1.overkiz.com/enduser-mobile-web/enduserAPI/",
        manufacturer="Somfy",
    ),
    "somfy_oceania": OverkizHub(
        name="Somfy (Oceania)",
        endpoint="https://ha201-1.overkiz.com/enduser-mobile-web/enduserAPI/",
        manufacturer="Somfy",
    ),
}
SUPPORTED_ENDPOINTS = {
    "Atlantic Cozytouch": "https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Hitachi Hi Kumo (Asia)": "https://ha203-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Hitachi Hi Kumo (Europe)": "https://ha117-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Hitachi Hi Kumo (Oceania)": "https://ha203-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Nexity Eugénie": "https://ha106-1.overkiz.com/enduser-mobile-web/enduserAPI",
    "Rexel Energeasy Connect": "https://ha112-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Somfy (Europe)": "https://tahomalink.com/enduser-mobile-web/enduserAPI/",  # uses https://ha101-1.overkiz.com
    "Somfy (North America)": "https://ha401-1.overkiz.com/enduser-mobile-web/enduserAPI/",
    "Somfy (Oceania)": "https://ha201-1.overkiz.com/enduser-mobile-web/enduserAPI/",
}

HUB_MANUFACTURER = {
    "Cozytouch": "Cozytouch",
    "Hitachi Hi Kumo (Asia)": "Hitachi",
    "Hitachi Hi Kumo (Europe)": "Hitachi",
    "Hitachi Hi Kumo (Oceania)": "Hitachi",
    "Nexity Eugénie": "Nexity",
    "Rexel Energeasy Connect": "Rexel",
    "Somfy (Europe)": "Somfy",
    "Somfy (Oceania)": "Somfy",
    "Somfy (North America)": "Somfy",
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
    "AtlanticElectricalHeaterWithAdjustableTemperatureSetpoint": CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    "AtlanticElectricalTowelDryer": CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    "AtlanticPassAPCDHW": CLIMATE,  # widgetName, uiClass is WaterHeatingSystem (not supported)
    "AtlanticPassAPCHeatingAndCoolingZone": CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    "AtlanticPassAPCZoneControl": CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
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
    "EvoHomeController": CLIMATE,  # widgetName, uiClass is EvoHome (not supported)
    "ExteriorScreen": COVER,
    "ExteriorVenetianBlind": COVER,
    "GarageDoor": COVER,
    "GasSensor": SENSOR,
    "Gate": COVER,
    "GenericSensor": SENSOR,
    "HeatingSetPoint": CLIMATE,  # widgetName, uiClass is EvoHome (not supported)
    "HitachiDHW": WATER_HEATER,  # widgetName, uiClass is HitachiHeatingSystem (not supported)
    "HitachiAirToWaterHeatingZone": CLIMATE,  # widgetName, uiClass is HitachiHeatingSystem (not supported)
    "HitachiAirToAirHeatPump": CLIMATE,  # widgetName, uiClass is HitachiHeatingSystem (not supported)
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
    "RTSGeneric": COVER,  # widgetName, uiClass is Generic (not supported)
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
