![screenshot of a device detail page in Home Assistant](https://raw.githubusercontent.com/iMicknl/ha-tahoma/master/media/tahoma_device_page.png)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/iMicknl/ha-tahoma.svg)](https://GitHub.com/iMicknl/ha-tahoma/releases/)

# Somfy TaHoma - Home Assistant

> The Tahoma integration platform is used as an interface to the tahomalink.com website. It adds covers, scenes and a sun sensor from the Tahoma platform.

This component builds upon the work of [@philklei](https://github.com/philklei) and is an updated version of his [original Tahoma integration](https://www.home-assistant.io/integrations/tahoma/) in Home Assistant with the goal of merging into core. The installation of this component will replace the original Tahoma integration and thus allows you to beta-test [all changes](./CHANGELOG.md).

## Supported Somfy gateways

- Somfy TaHoma Box
- Somfy Connexoon IO
- Somfy Connexoon RTS

## Installation

### Manual

Copy the `custom_components/tahoma` to your `custom_components` folder. Reboot Home Assistant and install the Somfy TaHoma integration via the integrations page.

### HACS

This integration is included in HACS. Search for the `Somfy TaHoma` integration and choose install. Reboot Home Assistant and install the Tahoma integration via the integrations page.

## Supported Somfy devices

This component doesn't have a hardcoded list of devices anymore, but relies on the `ui_class` of every Somfy device. This way more devices will be supported out of the box, based on their category, available states and commands.

| Somfy ui_class / widget      | Home Assistant platform |
| ---------------------------- | ----------------------- |
| AdjustableSlatsRollerShutter | cover                   |
| Alarm                        | alarm_control_panel     |
| AtlanticElectricalHeater     | climate                 |
| AirFlowSensor                | binary_sensor           |
| AirSensor                    | sensor                  |
| Awning                       | cover                   |
| CarButtonSensor              | binary_sensor           |
| ConsumptionSensor            | sensor                  |
| ContactSensor                | binary_sensor           |
| Curtain                      | cover                   |
| DimmerExteriorHeating        | climate                 |
| DoorLock                     | lock                    |
| ElectricitySensor            | sensor                  |
| ExteriorScreen               | cover                   |
| ExteriorVenetianBlind        | cover                   |
| GarageDoor                   | cover                   |
| GasSensor                    | sensor                  |
| Gate                         | cover                   |
| Generic                      | cover                   |
| GenericSensor                | sensor                  |
| HumiditySensor               | sensor                  |
| Light                        | light                   |
| LightSensor                  | sensor                  |
| MotionSensor                 | binary_sensor           |
| MyFoxSecurityCamera          | cover                   |
| OccupancySensor              | binary_sensor           |
| OnOff                        | switch                  |
| Pergola                      | cover                   |
| RainSensor                   | binary_sensor           |
| RollerShutter                | cover                   |
| Screen                       | cover                   |
| Shutter                      | cover                   |
| Siren                        | switch                  |
| SirenStatus                  | binary_sensor           |
| SmokeSensor                  | binary_sensor           |
| SomfyThermostat              | climate                 |
| SunIntensitySensor           | sensor                  |
| SunSensor                    | sensor                  |
| SwimmingPool                 | switch                  |
| SwingingShutter              | cover                   |
| TemperatureSensor            | sensor                  |
| ThermalEnergySensor          | sensor                  |
| VenetianBlind                | cover                   |
| WaterDetectionSensor         | binary_sensor           |
| WaterSensor                  | sensor                  |
| WeatherSensor                | sensor                  |
| WindSensor                   | sensor                  |
| Window                       | cover                   |
| WindowHandle                 | binary_sensor           |

## Advanced

### Enable debug logging

The [logger](https://www.home-assistant.io/integrations/logger/) integration lets you define the level of logging activities in Home Assistant. Turning on debug mode will show more information about unsupported devices in your logbook.

```yaml
logger:
  default: critical
  logs:
    custom_components.tahoma: debug
```

### Device not supported / working correctly

If your device is not visible in the device list of Home Assistant (/config/devices/dashboard), you need to turn on [debug logging](#enable-debug-logging). Copy the debug string and create a [new issue](https://github.com/iMicknl/ha-tahoma/issues/new/choose)

`DEBUG (MainThread) [custom_components.tahoma] Unsupported TaHoma device (io:DimmableLightIOComponent - Light - DimmableLight).`

If your device is listed in the device list, copy the firmware and create a [new issue](https://github.com/iMicknl/ha-tahoma/issues/new/choose). (e.g. io:DimmableLightIOComponent)

### Exclude devices

The previous component had functionality to exclude devices from Home Assistant. Since we moved to the entity registry, this functionality is now offered by default in Home Assistant core. You can now disable entities via the interface.
