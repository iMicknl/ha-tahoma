![](https://raw.githubusercontent.com/iMicknl/ha-tahoma/master/media/tahoma_device_page.png)

# Somfy TaHoma - Home Assistant (work in progress)

> The Tahoma integration platform is used as an interface to the tahomalink.com website. It adds covers, scenes and a sun sensor from the Tahoma platform.

This component is an updated version of the [original Tahoma integration](https://www.home-assistant.io/integrations/tahoma/) in Home Assistant and the goal is to get those changes merged in core. The installation of this component will replace the original Tahoma integration and thus allows you to beta-test [all changes](./CHANGELOG.md).

## Installation

### Manual

Copy the `custom_components/tahoma` to your `custom_components` folder. Reboot Home Assistant and install the Somfy TaHoma integration via the integrations page.

### HACS

Add the repository url below to HACS, search for the `Somfy TaHoma` integration and choose install. Reboot Home Assistant and install the Tahoma integration via the integrations page.

```
https://github.com/imicknl/ha-tahoma
```

## Supported devices

This component doesn't have a hardcoded list of devices anymore, but relies on the `uiclass` of every Somfy device. This way more devices will be supported out of the box, based on their category and available states and commands.

If your device is not supported, it will show the following message in the debug log. You can use this to create a new issue in the repository to see if the component can be added.

`DEBUG (MainThread) [custom_components.tahoma] Unsupported Tahoma device (internal:TSKAlarmComponent).`

| Somfy uiClass     | Home Assistant platform |
| ----------------- | ----------------------- |
| HeatingSystem     | climate                 |
| Awning            | cover                   |
| Curtain           | cover                   |
| ExteriorScreen    | cover                   |
| Gate              | cover                   |
| GarageDoor        | cover                   |
| Pergola           | cover                   |
| RollerShutter     | cover                   |
| SwingingShutter   | cover                   |
| Window            | cover                   |
| AirSensor         | sensor                  |
| ElectricitySensor | sensor                  |
| HumiditySensor    | sensor                  |
| LightSensor       | sensor                  |
| TemperatureSensor | sensor                  |
| DoorLock          | lock                    |
| OnOff             | switch                  |
| ContactSensor     | binary_sensor           |
| OccupancySensor   | binary_sensor           |
| SmokeSensor       | binary_sensor           |
| WindowHandle      | binary_sensor           |
| Light             | light                   |

## Not supported (yet)

| Somfy uiClass         |
| --------------------- |
| RemoteController      |
| Alarm                 |
| EvoHome               |
| HitachiHeatingSystem  |
| ExteriorHeatingSystem |
| Fan                   |
| Siren                 |
| MusicPlayer           |
| VentilationSystem     |

## Advanced

### Enable debug logging

The [logger](https://www.home-assistant.io/integrations/logger/) integration lets you define the level of logging activities in Home Assistant. Turning on debug mode will show more information about unsupported devices in your logbook.

```yaml
logger:
  default: critical
  logs:
    custom_components.tahoma: debug
```
