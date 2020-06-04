![](https://raw.githubusercontent.com/iMicknl/ha-tahoma/master/media/tahoma_device_page.png)

# Somfy Tahoma - Home Assistant (work in progress)

> The Tahoma integration platform is used as an interface to the tahomalink.com website. It adds covers, scenes and a sun sensor from the Tahoma platform.

This component is an updated version of the [original Tahoma integration](https://www.home-assistant.io/integrations/tahoma/) in Home Assistant and the goal is to get those changes merged in core. The installation of this component will replace the original Tahoma integration and thus allows you to beta-test [all changes](./CHANGELOG.md).

## Installation

### Manual

Copy the `custom_components/tahoma` to your `custom_components` folder. Reboot home assistant and install the Tahoma integration via the integrations config flow.

### HACS

Add the repository url below to HACS, search for the `Tahoma` integration and choose install. Reboot home assistant and install the Tahoma integration via the integrations config flow.

```
https://github.com/imicknl/ha-tahoma
```

## Supported devices

This component doesn't have a hardcoded list of devices anymore, but relies on the `uiclass` of every Somfy device. This way more devices will be supported out of the box, based on their category and available states and commands.

If your device is not supported, it will show the following message in the logging. You can use this to create a new issue in the repository to see if the component can be added.
`Unsupported Tahoma device (internal:TSKAlarmComponent - Alarm - TSKAlarmController)`

| Somfy uiClass     | Home Assistant platform |
| ----------------- | ----------------------- |
| ExteriorScreen    | cover                   |
| Pergola           | cover                   |
| RollerShutter     | cover                   |
| Window            | cover                   |
| TemperatureSensor | sensor                  |
| HumiditySensor    | sensor                  |
| DoorLock          | lock                    |
| OnOff             | switch                  |
| LightSensor       | sensor                  |
| GarageDoor        | cover                   |
| ContactSensor     | binary_sensor           |
| SmokeSensor       | binary_sensor           |
| OccupancySensor   | binary_sensor           |
| Light             | light                   |
| Awning            | cover                   |
| Alarm             | alarm_control_panel     |

## Not supported (yet)

| Somfy uiClass    |
| ---------------- |
| RemoteController |
| HeatingSystem    |
