![Details page of an awning](https://user-images.githubusercontent.com/8216238/132857336-ee7c719e-498c-49f9-adc2-017305b7bc7e.png)


[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/iMicknl/ha-tahoma.svg)](https://GitHub.com/iMicknl/ha-tahoma/releases/)
[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/iMicknl/ha-tahoma/)
[![Discord](https://img.shields.io/discord/718361810985549945?label=chat&logo=discord)](https://discord.gg/RRXuSVDAzG)

# Overkiz (by Somfy) - Home Assistant

Custom component for Home Assistant to interact with smart devices via the Overkiz platform.

>This component is an updated version of the [original Tahoma integration](https://www.home-assistant.io/integrations/tahoma/) in Home Assistant with the goal of eventually merging into core. The installation of this component will replace the original TaHoma integration and thus allows you to beta-test [all changes](https://github.com/iMicknl/ha-tahoma/releases).

## Supported hubs

- Somfy TaHoma
- Somfy TaHoma Switch [(instructions)](#tahoma-switch)
- Somfy Connexoon IO
- Somfy Connexoon RTS
- Atlantic Cozytouch
- Hitachi Hi Kumo
- Rexel Energeasy Connect
- Nexity Eugénie

### TaHoma Switch

Multiple users reported that the TaHoma Switch will work with this integration **after** you create a scene in the TaHoma app and wait for a few hours. See [#507](https://github.com/iMicknl/ha-tahoma/issues/507) for context.

## Supported devices

Most of the devices supported by your hub should be supported. If it is not the case or working correctly, have a look [here](#device-not-supported--working-correctly).

## Installation

You can install this integration via [HACS](#hacs) or [manually](#manual).

### HACS

This integration is included in HACS. Search for the `Overkiz (by Somfy)` integration and choose install. Reboot Home Assistant and configure the 'Overkiz (by Somfy)' integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=tahoma)

### Manual

Copy the `custom_components/tahoma` to your `custom_components` folder. Reboot Home Assistant and configure the 'Overkiz (by Somfy)' integration via the integrations page or press the blue button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=tahoma)


## Advanced

### Available services

After installation this integration adds new services to Home Assistant which can be used in automations. The new services are:

+ Overkiz (by Somfy): Set cover position with low speed (tahoma.set_cover_position_low_speed, only added if supported by the device)
+ Overkiz (by Somfy): My position (cover) (tahoma.set_cover_my_position)
+ Overkiz (by Somfy): Execute command (tahoma.execute_command)
+ Overkiz (by Somfy): Get execution history (tahoma.get_execution_history)

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

### Retrieve HomeKit code

If your hub (e.g. Somfy TaHoma) supports HomeKit natively, your setup code will be added as a sensor in Home Assistant. Look up your hub in Home Assistant and retrieve the value from the 'HomeKit Setup Code' sensor. You can now configure the [HomeKit Controller](https://www.home-assistant.io/integrations/homekit_controller/) integration in Home Assistant.
