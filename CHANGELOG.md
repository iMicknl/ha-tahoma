# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added support for RainSensor
- Added support for WaterDetectionSensor
- Added basic support for Siren as switch
- Added support for MotionSensor
- Added all available states to device state attributes

### Changed

- Change 'battery_level' attribute to an integer, estimated based on the battery state
- Changed CO2Sensor device class to co2 to show as co2 sensor in HomeKit  

## [1.4] - 22-06-2020

### Added

- Added support for HeatingSystem devices
- Added support for Gate devices
- Added support for AirSensor devices
- Added support for ElectricitySensor devices
- Added support for TemperatureSensor devices
- Added support for Curtain devices
- Added support for Generic devices (cover)
- Added support for SwingingShutter devices
- Added support for 'up' and 'down' commands for covers
- Added tilt_position support for covers
- Added support for 'setRGB' commands for lights

### Changed

- Removed all hardcoded device strings from the cover component
- Update state after a command has been succesfully executed

## [1.0.0] - 04-06-2020

### Added

- Added configuration flow
- Added support for controlling the tilt position of supported covers
- Added support for Somfy devices using the Pergola uiclass.
- Added unique id per entity, making it configurable via the front-end.
- Added support for Humidity sensors
- Added support for Light (DimmableLight) devices

### Changed

- Changed MotionSensor platform from sensor to binary_sensor
- Changed SmokeSensor platform from sensor to binary_sensor
- Changed ContactSensor platform from sensor to binary_sensor
- Changed GarageDoor platform from switch to cover
- Changed Light (OnOffLight) platform from switch to light
- Changed cover implementation to rely on available states and commands, instead of a hardcoded device list
- Add shared device attributes and states to TahomaDevice
