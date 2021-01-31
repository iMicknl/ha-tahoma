![screenshot of a device detail page in Home Assistant](https://raw.githubusercontent.com/iMicknl/ha-tahoma/master/media/tahoma_device_page.png)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/iMicknl/ha-tahoma.svg)](https://GitHub.com/iMicknl/ha-tahoma/releases/)

# Somfy TaHoma - Home Assistant

Custom component for Home Assistant to interact with smart devices via the Somfy TaHoma platform. Despite the name of this integration, many other platforms sharing the same OverKiz API structure are supported as well. Have a look at all [supported hubs](#supported-hubs).

>This component builds upon the work of [@philklei](https://github.com/philklei) and is an updated version of the [original Tahoma integration](https://www.home-assistant.io/integrations/tahoma/) in Home Assistant with the goal of eventually merging into core. The installation of this component will replace the original TaHoma integration and thus allows you to beta-test [all changes](https://github.com/iMicknl/ha-tahoma/releases).

## Supported hubs

- Somfy TaHoma Box
- Somfy Connexoon IO
- Somfy Connexoon RTS
- Cozytouch
- Hi Kumo
- Rexel
- eedomus

## Supported devices

This integration doesn't rely on a hardcoded list of devices anymore, but relies on the characteristics of every device. This means that more devices will be supported out of the box, based on their category, available states and commands. If your device is not supported or working correctly, have a look [here](#device-not-supported--working-correctly).

## Installation

### Manual

Copy the `custom_components/tahoma` to your `custom_components` folder. Reboot Home Assistant and install the Somfy TaHoma integration via the integrations page.

### HACS

This integration is included in HACS. Search for the `Somfy TaHoma` integration and choose install. Reboot Home Assistant and install the Tahoma integration via the integrations page.

## Advanced

### Enable debug logging

The [logger](https://www.home-assistant.io/integrations/logger/) integration lets you define the level of logging activities in Home Assistant. Turning on debug mode will show more information about unsupported devices in your logbook.

```yaml
logger:
  default: critical
  logs:
    custom_components.tahoma: debug
```

### Device not supported

If your device is not visible in the device list of Home Assistant (/config/devices/dashboard), you need to turn on [debug logging](#enable-debug-logging). Copy the debug string from your log and create a [new issue](https://github.com/iMicknl/ha-tahoma/issues/new/choose)

`DEBUG (MainThread) [custom_components.tahoma] Unsupported TaHoma device (io:DimmableLightIOComponent - Light - DimmableLight).`

### Device not working correctly

If your device is listed in the device list, create a [new issue](https://github.com/iMicknl/ha-tahoma/issues/new/choose) and fill in all details of the issue template.

In order to gather more information, you can use the `tahoma.get_execution_history` service which will print your execution history to the Home Assistant log. Run the commands via the official vendor app (e.g. TaHoma) and capture the commands.

```
2021-01-28 09:20:22 INFO (MainThread) [custom_components.tahoma] 2021-01-27 21:30:00: off executed via Home Assistant on io://xxxx, with [].
2021-01-28 09:20:22 INFO (MainThread) [custom_components.tahoma] 2021-01-27 16:23:29: setIntensity executed via Home Assistant on io://xxxx, with [70].
```

### Exclude devices

The previous version had functionality to exclude devices from Home Assistant. Since we moved to the entity registry, this functionality is now offered by default in Home Assistant core. You can now disable entities via the interface.

### Retrieve HomeKit code

If your TaHoma box supports HomeKit natively, the integration will log the HomeKit code on start currently. This is currently an experimental implementation and in order to enable this, you need to have debug logging enabled.
