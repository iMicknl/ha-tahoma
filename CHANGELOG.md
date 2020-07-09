# Changelog

## [Unreleased](https://github.com/iMicknl/ha-tahoma/tree/HEAD)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.5...HEAD)

**Breaking changes:**

- Remove obsolete YAML schema [\#120](https://github.com/iMicknl/ha-tahoma/pull/120) ([iMicknl](https://github.com/iMicknl))

**Implemented enhancements:**

- Retrieve core:MeasuredValueType to understand if it is Celsius or Kelvin [\#111](https://github.com/iMicknl/ha-tahoma/issues/111)
- Move constants outside of const.py [\#125](https://github.com/iMicknl/ha-tahoma/pull/125) ([vlebourl](https://github.com/vlebourl))
- Hide opg device from log. [\#117](https://github.com/iMicknl/ha-tahoma/pull/117) ([vlebourl](https://github.com/vlebourl))
- Parse temperature unit for TemperatureSensor [\#116](https://github.com/iMicknl/ha-tahoma/pull/116) ([vlebourl](https://github.com/vlebourl))
- Remove lock variables from Cover device state attributes [\#108](https://github.com/iMicknl/ha-tahoma/pull/108) ([tetienne](https://github.com/tetienne))
- Split update cover method [\#106](https://github.com/iMicknl/ha-tahoma/pull/106) ([tetienne](https://github.com/tetienne))
- Add support for more sensors & basic Siren \(switch\) support [\#84](https://github.com/iMicknl/ha-tahoma/pull/84) ([iMicknl](https://github.com/iMicknl))

**Closed issues:**

- Remove YAML config schema [\#113](https://github.com/iMicknl/ha-tahoma/issues/113)
- Add support for RainSensor \(io:SomfyRainIOSystemSensor\) [\#102](https://github.com/iMicknl/ha-tahoma/issues/102)

**Merged pull requests:**

- Create CODEOWNERS [\#129](https://github.com/iMicknl/ha-tahoma/pull/129) ([tetienne](https://github.com/tetienne))
- Remove all self.\_\* variables in cover module [\#128](https://github.com/iMicknl/ha-tahoma/pull/128) ([tetienne](https://github.com/tetienne))
- Fixed a typo. [\#124](https://github.com/iMicknl/ha-tahoma/pull/124) ([vlebourl](https://github.com/vlebourl))
- Add an auto changelog issue [\#123](https://github.com/iMicknl/ha-tahoma/pull/123) ([vlebourl](https://github.com/vlebourl))
- Code readability improvements [\#121](https://github.com/iMicknl/ha-tahoma/pull/121) ([iMicknl](https://github.com/iMicknl))

## [1.5](https://github.com/iMicknl/ha-tahoma/tree/1.5) (2020-07-03)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.5-alpha2...1.5)

**Fixed bugs:**

- custom\_components.tahoma.config\_flow - Unexpected exception - ValueError: No ui Class [\#99](https://github.com/iMicknl/ha-tahoma/issues/99)
- Update for light component \(rgb\) fails - error in logs [\#96](https://github.com/iMicknl/ha-tahoma/issues/96)
- Not authenticated error. [\#86](https://github.com/iMicknl/ha-tahoma/issues/86)
- Remove exception raising in Device `\_\_init\_\_` in the API [\#101](https://github.com/iMicknl/ha-tahoma/pull/101) ([vlebourl](https://github.com/vlebourl))
- Fix a test in api login. [\#100](https://github.com/iMicknl/ha-tahoma/pull/100) ([vlebourl](https://github.com/vlebourl))

## [1.5-alpha2](https://github.com/iMicknl/ha-tahoma/tree/1.5-alpha2) (2020-07-02)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.5-alpha1...1.5-alpha2)

**Fixed bugs:**

- \[fix\] color\_RGB\_to\_hs is missing parameters [\#97](https://github.com/iMicknl/ha-tahoma/pull/97) ([vlebourl](https://github.com/vlebourl))
- Re-log in the API after a "error":"Not authenticated" [\#95](https://github.com/iMicknl/ha-tahoma/pull/95) ([vlebourl](https://github.com/vlebourl))
- Bugfix for unable to change tilt position on io:BioclimaticPergolaIOComponent \#74 [\#77](https://github.com/iMicknl/ha-tahoma/pull/77) ([iMicknl](https://github.com/iMicknl))

## [1.5-alpha1](https://github.com/iMicknl/ha-tahoma/tree/1.5-alpha1) (2020-07-02)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4.1...1.5-alpha1)

**Fixed bugs:**

- Actions are applied sequentialy [\#92](https://github.com/iMicknl/ha-tahoma/issues/92)
- Covers move step by step and can't be stopped while moving [\#90](https://github.com/iMicknl/ha-tahoma/issues/90)
- Remove the lock on apply\_action [\#93](https://github.com/iMicknl/ha-tahoma/pull/93) ([vlebourl](https://github.com/vlebourl))

## [1.4.1](https://github.com/iMicknl/ha-tahoma/tree/1.4.1) (2020-07-01)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4...1.4.1)

**Implemented enhancements:**

- Add climate platform [\#12](https://github.com/iMicknl/ha-tahoma/issues/12)
- Add active\_states to device\_state\_attributes [\#89](https://github.com/iMicknl/ha-tahoma/pull/89) ([vlebourl](https://github.com/vlebourl))

**Fixed bugs:**

- fix api for missing states at login [\#94](https://github.com/iMicknl/ha-tahoma/pull/94) ([vlebourl](https://github.com/vlebourl))
- \[fix\] fix AttributeError: 'NoneType' object has no attribute 'state' … [\#87](https://github.com/iMicknl/ha-tahoma/pull/87) ([vlebourl](https://github.com/vlebourl))
- Add part of fix\_44 changes already [\#82](https://github.com/iMicknl/ha-tahoma/pull/82) ([iMicknl](https://github.com/iMicknl))

## [1.4](https://github.com/iMicknl/ha-tahoma/tree/1.4) (2020-06-22)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4-alpha3...1.4)

**Implemented enhancements:**

- Electricity Meter [\#80](https://github.com/iMicknl/ha-tahoma/issues/80)
- Add support for IO RGB Light \(io:DimmableRGBLightIOComponent\) [\#73](https://github.com/iMicknl/ha-tahoma/issues/73)
- Change Unsupported Tahoma device logging from `warning` to `debug` [\#32](https://github.com/iMicknl/ha-tahoma/issues/32)
- Adjust code style according to home-assistant/core [\#20](https://github.com/iMicknl/ha-tahoma/issues/20)
- \[feat\] Support io:TotalElectricalEnergyConsumptionIOSystemSensor [\#81](https://github.com/iMicknl/ha-tahoma/pull/81) ([vlebourl](https://github.com/vlebourl))
- Update cover & changelog [\#78](https://github.com/iMicknl/ha-tahoma/pull/78) ([iMicknl](https://github.com/iMicknl))
- Wait for apply\_action to finish before returning. [\#76](https://github.com/iMicknl/ha-tahoma/pull/76) ([vlebourl](https://github.com/vlebourl))
- Add support for "setRGB" command for light entity. [\#75](https://github.com/iMicknl/ha-tahoma/pull/75) ([vlebourl](https://github.com/vlebourl))
- Add climate entity for Somfy's Smart Thermostat [\#54](https://github.com/iMicknl/ha-tahoma/pull/54) ([vlebourl](https://github.com/vlebourl))

**Fixed bugs:**

- Unable to change tilt position on io:BioclimaticPergolaIOComponent [\#74](https://github.com/iMicknl/ha-tahoma/issues/74)
- Bugfix for unable to change tilt position on io:BioclimaticPergolaIOComponent \#74 [\#77](https://github.com/iMicknl/ha-tahoma/pull/77) ([iMicknl](https://github.com/iMicknl))

## [1.4-alpha3](https://github.com/iMicknl/ha-tahoma/tree/1.4-alpha3) (2020-06-18)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4-alpha2...1.4-alpha3)

**Fixed bugs:**

- fixed a typo [\#72](https://github.com/iMicknl/ha-tahoma/pull/72) ([vlebourl](https://github.com/vlebourl))

## [1.4-alpha2](https://github.com/iMicknl/ha-tahoma/tree/1.4-alpha2) (2020-06-18)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4-alpha1...1.4-alpha2)

**Implemented enhancements:**

- Detected I/O inside the event loop. This is causing stability issues.  [\#2](https://github.com/iMicknl/ha-tahoma/issues/2)
- up/down as alternatives to open/close [\#71](https://github.com/iMicknl/ha-tahoma/pull/71) ([vlebourl](https://github.com/vlebourl))

## [1.4-alpha1](https://github.com/iMicknl/ha-tahoma/tree/1.4-alpha1) (2020-06-17)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.3...1.4-alpha1)

## [1.3](https://github.com/iMicknl/ha-tahoma/tree/1.3) (2020-06-17)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.2...1.3)

**Implemented enhancements:**

- Support disabling of entities, for use with Somfy integration [\#17](https://github.com/iMicknl/ha-tahoma/issues/17)
- Make assumed\_state for RTS configurable via option flow [\#9](https://github.com/iMicknl/ha-tahoma/issues/9)
- adds async\_apply\_action [\#70](https://github.com/iMicknl/ha-tahoma/pull/70) ([vlebourl](https://github.com/vlebourl))
- Added stack trace [\#65](https://github.com/iMicknl/ha-tahoma/pull/65) ([vlebourl](https://github.com/vlebourl))
- Change `turn\_on` and `turn\_off` to sync calls  [\#64](https://github.com/iMicknl/ha-tahoma/pull/64) ([vlebourl](https://github.com/vlebourl))
- Enable debug logging, remove warnings [\#63](https://github.com/iMicknl/ha-tahoma/pull/63) ([iMicknl](https://github.com/iMicknl))
- Update light.py [\#60](https://github.com/iMicknl/ha-tahoma/pull/60) ([vlebourl](https://github.com/vlebourl))
- Add new device types [\#58](https://github.com/iMicknl/ha-tahoma/pull/58) ([iMicknl](https://github.com/iMicknl))
- Schedule devices update right after it's added [\#53](https://github.com/iMicknl/ha-tahoma/pull/53) ([vlebourl](https://github.com/vlebourl))
- Added device\_class to sensors [\#51](https://github.com/iMicknl/ha-tahoma/pull/51) ([vlebourl](https://github.com/vlebourl))
- Enable scenes [\#50](https://github.com/iMicknl/ha-tahoma/pull/50) ([iMicknl](https://github.com/iMicknl))

**Fixed bugs:**

- Error unloading entry xxxxxx for tahoma [\#61](https://github.com/iMicknl/ha-tahoma/issues/61)
- Add support for Tahoma Scenes [\#47](https://github.com/iMicknl/ha-tahoma/issues/47)
- Fix \#61 [\#62](https://github.com/iMicknl/ha-tahoma/pull/62) ([vlebourl](https://github.com/vlebourl))
- Tahoma seems to not send all possible keys, depending on the devices … [\#52](https://github.com/iMicknl/ha-tahoma/pull/52) ([vlebourl](https://github.com/vlebourl))
- Fix domain [\#49](https://github.com/iMicknl/ha-tahoma/pull/49) ([iMicknl](https://github.com/iMicknl))

**Closed issues:**

- Add support for OccupancySensor \(io:SomfyOccupancyIOSystemSensor\) [\#19](https://github.com/iMicknl/ha-tahoma/issues/19)

**Merged pull requests:**

- fixes get\_events [\#55](https://github.com/iMicknl/ha-tahoma/pull/55) ([vlebourl](https://github.com/vlebourl))
- renamed tahoma or Tahoma to TaHoma. [\#46](https://github.com/iMicknl/ha-tahoma/pull/46) ([vlebourl](https://github.com/vlebourl))
- Add french translation [\#45](https://github.com/iMicknl/ha-tahoma/pull/45) ([vlebourl](https://github.com/vlebourl))

## [1.2](https://github.com/iMicknl/ha-tahoma/tree/1.2) (2020-06-07)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.1...1.2)

**Implemented enhancements:**

- Add better exception handling & retry logic for Tahoma API [\#4](https://github.com/iMicknl/ha-tahoma/issues/4)
- Refactored requests to avoid being locked out of the api. [\#24](https://github.com/iMicknl/ha-tahoma/pull/24) ([vlebourl](https://github.com/vlebourl))

**Fixed bugs:**

- Position is not updated - PositionableHorizontalAwning - io:HorizontalAwningIOComponent [\#30](https://github.com/iMicknl/ha-tahoma/issues/30)
- ValueError: Config entry has already been setup! [\#16](https://github.com/iMicknl/ha-tahoma/issues/16)
- Reverse position for PositionableHorizontalAwning [\#41](https://github.com/iMicknl/ha-tahoma/pull/41) ([iMicknl](https://github.com/iMicknl))
- Fix ValueError: Config entry has already been setup! \#16 [\#35](https://github.com/iMicknl/ha-tahoma/pull/35) ([iMicknl](https://github.com/iMicknl))

**Closed issues:**

- Add support for Gate - DiscreteGateWithPedestrianPosition \(io:DiscreteGateOpenerIOComponent\) [\#18](https://github.com/iMicknl/ha-tahoma/issues/18)

**Merged pull requests:**

- fixed a typo [\#38](https://github.com/iMicknl/ha-tahoma/pull/38) ([vlebourl](https://github.com/vlebourl))
- Rename to Somfy TaHoma [\#37](https://github.com/iMicknl/ha-tahoma/pull/37) ([iMicknl](https://github.com/iMicknl))
- Rename to Somfy TaHoma [\#36](https://github.com/iMicknl/ha-tahoma/pull/36) ([iMicknl](https://github.com/iMicknl))

## [1.1](https://github.com/iMicknl/ha-tahoma/tree/1.1) (2020-06-07)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.1-alpha2...1.1)

**Implemented enhancements:**

- Refactor cover platform, removed hardcoded references [\#8](https://github.com/iMicknl/ha-tahoma/issues/8)

**Fixed bugs:**

- `TahomaLight` object has no attribute `\_brightness` [\#22](https://github.com/iMicknl/ha-tahoma/issues/22)
- Fix faulty if statement [\#34](https://github.com/iMicknl/ha-tahoma/pull/34) ([iMicknl](https://github.com/iMicknl))
- Fix TahomaLight` object has no attribute `\_brightness [\#29](https://github.com/iMicknl/ha-tahoma/pull/29) ([iMicknl](https://github.com/iMicknl))

## [1.1-alpha2](https://github.com/iMicknl/ha-tahoma/tree/1.1-alpha2) (2020-06-05)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.1-alpha...1.1-alpha2)

**Implemented enhancements:**

- Refactor cover platform [\#13](https://github.com/iMicknl/ha-tahoma/pull/13) ([iMicknl](https://github.com/iMicknl))

## [1.1-alpha](https://github.com/iMicknl/ha-tahoma/tree/1.1-alpha) (2020-06-04)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.0.0...1.1-alpha)

**Implemented enhancements:**

- Add support for scenes [\#10](https://github.com/iMicknl/ha-tahoma/issues/10)
- Incorporate changes from tahoma\_extended [\#5](https://github.com/iMicknl/ha-tahoma/issues/5)
- Add occupancy sensor and start fixing async [\#15](https://github.com/iMicknl/ha-tahoma/pull/15) ([iMicknl](https://github.com/iMicknl))
- Add support for scenes [\#14](https://github.com/iMicknl/ha-tahoma/pull/14) ([iMicknl](https://github.com/iMicknl))

## [1.0.0](https://github.com/iMicknl/ha-tahoma/tree/1.0.0) (2020-06-04)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/014ff6a7acc5ca5a88cd78f695b7505ca2f01f1e...1.0.0)

**Implemented enhancements:**

- Support Awning devices and update readme + changelog [\#11](https://github.com/iMicknl/ha-tahoma/pull/11) ([iMicknl](https://github.com/iMicknl))
- Apply fixes from tahoma\_extended & sensor/binary sensor improvements [\#7](https://github.com/iMicknl/ha-tahoma/pull/7) ([iMicknl](https://github.com/iMicknl))
- Add binary sensor and remove parts from normal sensor [\#6](https://github.com/iMicknl/ha-tahoma/pull/6) ([iMicknl](https://github.com/iMicknl))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
