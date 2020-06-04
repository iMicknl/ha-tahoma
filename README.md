# Tahoma (work in progress)

> The Tahoma integration platform is used as an interface to the tahomalink.com website. It adds covers, scenes and a sun sensor from the Tahoma platform.

This component is an updated version of the original Tahoma integration in Home Assistant and the goal is to get those changes merged in core. The installation of this component will replace the original Tahoma integration and thus allows you to beta-test the new changes.

# Supported devices

The Tahoma component doesn't have a hardcoded list of devices anymore, but relies on the `uiclass` of every Somfy device.

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
| Light             | light                   |

## Installation

### Manual

Copy the `custom_components/tahoma` to your `custom_components` folder. Reboot home assistant and install the Tahoma integration via the integrations config flow.

### HACS

Add the repository url below to HACS, search for the `Tahoma` integration and choose install. Reboot home assistant and install the Tahoma integration via the integrations config flow.

```
https://github.com/imicknl/ha-tahoma
```
