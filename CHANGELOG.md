# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0]

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