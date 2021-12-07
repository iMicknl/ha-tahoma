"""Constants for the Overkiz (by Somfy) integration."""
from datetime import timedelta
from typing import Final

from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_CONTROL_PANEL
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR
from homeassistant.components.button import DOMAIN as BUTTON
from homeassistant.components.climate import DOMAIN as CLIMATE
from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.light import DOMAIN as LIGHT
from homeassistant.components.lock import DOMAIN as LOCK
from homeassistant.components.number import DOMAIN as NUMBER
from homeassistant.components.scene import DOMAIN as SCENE
from homeassistant.components.select import DOMAIN as SELECT
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.components.switch import DOMAIN as SWITCH
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER
from pyhoma.enums import UIClass, UIWidget

DOMAIN: Final = "tahoma"

CONF_HUB = "hub"
DEFAULT_HUB = "somfy_europe"

UPDATE_INTERVAL = timedelta(seconds=30)
UPDATE_INTERVAL_ALL_ASSUMED_STATE = timedelta(minutes=60)

SUPPORTED_PLATFORMS = [
    ALARM_CONTROL_PANEL,
    BINARY_SENSOR,
    BUTTON,
    CLIMATE,
    COVER,
    LIGHT,
    LOCK,
    NUMBER,
    SCENE,
    SELECT,
    SENSOR,
    SWITCH,
    WATER_HEATER,
]

IGNORED_OVERKIZ_DEVICES = [
    UIClass.PROTOCOL_GATEWAY,
    UIClass.POD,
]

# Used to map the Somfy widget and ui_class to the Home Assistant platform
OVERKIZ_DEVICE_TO_PLATFORM = {
    UIClass.ADJUSTABLE_SLATS_ROLLER_SHUTTER: COVER,
    UIClass.ALARM: ALARM_CONTROL_PANEL,
    UIWidget.ATLANTIC_ELECTRICAL_HEATER: CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    UIWidget.ATLANTIC_ELECTRICAL_HEATER_WITH_ADJUSTABLE_TEMPERATURE_SETPOINT: CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    UIWidget.ATLANTIC_ELECTRICAL_TOWEL_DRYER: CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    UIWidget.ATLANTIC_PASS_APC_DHW: CLIMATE,  # widgetName, uiClass is WaterHeatingSystem (not supported)
    UIWidget.ATLANTIC_PASS_APC_HEATING_AND_COOLING_ZONE: CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    UIWidget.ATLANTIC_PASS_APC_ZONE_CONTROL: CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    UIClass.AWNING: COVER,
    UIClass.CURTAIN: COVER,
    UIWidget.DIMMER_EXTERIOR_HEATING: CLIMATE,  # widgetName, uiClass is ExteriorHeatingSystem (not supported)
    UIWidget.DOMESTIC_HOT_WATER_PRODUCTION: WATER_HEATER,  # widgetName, uiClass is WaterHeatingSystem (not supported)
    UIWidget.DOMESTIC_HOT_WATER_TANK: SWITCH,  # widgetName, uiClass is WaterHeatingSystem (not supported)
    UIClass.DOOR_LOCK: LOCK,
    UIWidget.EVO_HOME_CONTROLLER: CLIMATE,  # widgetName, uiClass is EvoHome (not supported)
    UIClass.EXTERIOR_SCREEN: COVER,
    UIClass.EXTERIOR_VENETIAN_BLIND: COVER,
    UIClass.GARAGE_DOOR: COVER,
    UIClass.GATE: COVER,
    UIWidget.HEATING_SET_POINT: CLIMATE,  # widgetName, uiClass is EvoHome (not supported)
    UIWidget.HITACHI_DHW: WATER_HEATER,  # widgetName, uiClass is HitachiHeatingSystem (not supported)
    UIWidget.HITACHI_AIR_TO_WATER_HEATING_ZONE: CLIMATE,  # widgetName, uiClass is HitachiHeatingSystem (not supported)
    UIWidget.HITACHI_AIR_TO_AIR_HEAT_PUMP: CLIMATE,  # widgetName, uiClass is HitachiHeatingSystem (not supported)
    UIClass.LIGHT: LIGHT,
    UIWidget.MY_FOX_SECURITY_CAMERA: COVER,  # widgetName, uiClass is Camera (not supported)
    UIClass.ON_OFF: SWITCH,
    UIClass.PERGOLA: COVER,
    UIClass.ROLLER_SHUTTER: COVER,
    UIWidget.RTS_GENERIC: COVER,  # widgetName, uiClass is Generic (not supported)
    UIClass.SCREEN: COVER,
    UIClass.SHUTTER: COVER,
    UIClass.SIREN: SWITCH,
    UIWidget.SIREN_STATUS: None,  # widgetName, uiClass is Siren (switch)
    UIWidget.SOMFY_THERMOSTAT: CLIMATE,  # widgetName, uiClass is HeatingSystem (not supported)
    UIWidget.STATELESS_EXTERIOR_HEATING: CLIMATE,  # widgetName, uiClass is ExteriorHeatingSystem.
    UIClass.SWIMMING_POOL: SWITCH,
    UIClass.SWINGING_SHUTTER: COVER,
    UIClass.VENETIAN_BLIND: COVER,
    UIClass.WINDOW: COVER,
}
