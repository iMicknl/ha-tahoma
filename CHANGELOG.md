# Changelog

## [Unreleased](https://github.com/iMicknl/ha-tahoma/tree/HEAD)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v2.0.2...HEAD)

🐛 **Bug Fixes**

- Sliding gate not working [\#234](https://github.com/iMicknl/ha-tahoma/issues/234)

**Closed issues:**

- Add support for StatefulAlarmController \(io:AlarmIOComponent\) [\#218](https://github.com/iMicknl/ha-tahoma/issues/218)
- Add support for StatelessAlarmController \(rtd:AlarmRTDComponent\) [\#217](https://github.com/iMicknl/ha-tahoma/issues/217)
- Add support for AlarmPanelController \(verisure:GenericAlarmPanel\) [\#216](https://github.com/iMicknl/ha-tahoma/issues/216)
- Add support for MyFoxAlarmController \(myfox:SomfyProtectAlarmController\) [\#215](https://github.com/iMicknl/ha-tahoma/issues/215)
- Add support for TSKAlarmController \(internal:TSKAlarmComponent\) [\#212](https://github.com/iMicknl/ha-tahoma/issues/212)

## [v2.0.2](https://github.com/iMicknl/ha-tahoma/tree/v2.0.2) (2020-08-20)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v2.1.0...v2.0.2)

## [v2.1.0](https://github.com/iMicknl/ha-tahoma/tree/v2.1.0) (2020-08-20)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v2.0.1...v2.1.0)

✨ **Enhancement**

- Add tests for config flow [\#3](https://github.com/iMicknl/ha-tahoma/issues/3)
- Support opening and closing the cover of MyFoxSecurityCamera  [\#224](https://github.com/iMicknl/ha-tahoma/pull/224) ([iMicknl](https://github.com/iMicknl))
- Add alarm integration [\#214](https://github.com/iMicknl/ha-tahoma/pull/214) ([iMicknl](https://github.com/iMicknl))
- Add first unit tests for Config Flow [\#213](https://github.com/iMicknl/ha-tahoma/pull/213) ([iMicknl](https://github.com/iMicknl))

🐛 **Bug Fixes**

- Log is not containing all the devices I have. [\#207](https://github.com/iMicknl/ha-tahoma/issues/207)
- Fix crash when using faulty / disabled ZWave devices [\#232](https://github.com/iMicknl/ha-tahoma/pull/232) ([iMicknl](https://github.com/iMicknl))

**Closed issues:**

- No state update for lights [\#229](https://github.com/iMicknl/ha-tahoma/issues/229)
- Add support for Somfy Outdoor Camera \(myfox:SomfyProtectSecurityCameraController\) [\#222](https://github.com/iMicknl/ha-tahoma/issues/222)
- Add support for SomfyOneplusCamera \(myfox:SomfyOnePlusCameraController\) [\#221](https://github.com/iMicknl/ha-tahoma/issues/221)

## [v2.0.1](https://github.com/iMicknl/ha-tahoma/tree/v2.0.1) (2020-08-06)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v2.0.0...v2.0.1)

🐛 **Bug Fixes**

- Bump pyhoma to 0.3.2 [\#210](https://github.com/iMicknl/ha-tahoma/pull/210) ([tetienne](https://github.com/tetienne))
- Match climate devices on their widgetName [\#209](https://github.com/iMicknl/ha-tahoma/pull/209) ([iMicknl](https://github.com/iMicknl))

## [v2.0.0](https://github.com/iMicknl/ha-tahoma/tree/v2.0.0) (2020-08-05)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v1.6.4...v2.0.0)

✨ **Enhancement**

- Support multiple types of boxes with different API endpoints. [\#85](https://github.com/iMicknl/ha-tahoma/issues/85)
- Refactor update methods to use single DataUpdateCoordinator [\#1](https://github.com/iMicknl/ha-tahoma/issues/1)
- Support YAML configuration  [\#201](https://github.com/iMicknl/ha-tahoma/pull/201) ([iMicknl](https://github.com/iMicknl))
- Create constant for ignored devices [\#200](https://github.com/iMicknl/ha-tahoma/pull/200) ([tetienne](https://github.com/tetienne))
- Various small clean [\#199](https://github.com/iMicknl/ha-tahoma/pull/199) ([tetienne](https://github.com/tetienne))
- Reduce platform setup complexity [\#198](https://github.com/iMicknl/ha-tahoma/pull/198) ([tetienne](https://github.com/tetienne))
- Improve climate platform and support dynamic state allocation [\#197](https://github.com/iMicknl/ha-tahoma/pull/197) ([tetienne](https://github.com/tetienne))
- Remove SCAN\_INTERVAL in favour of DataUpdateCoordinator [\#195](https://github.com/iMicknl/ha-tahoma/pull/195) ([iMicknl](https://github.com/iMicknl))
- Enable position for AdjustableSlatsRollerShutter devices [\#192](https://github.com/iMicknl/ha-tahoma/pull/192) ([iMicknl](https://github.com/iMicknl))
- Pin pyhoma package and change tahoma\_api to pyhoma [\#190](https://github.com/iMicknl/ha-tahoma/pull/190) ([iMicknl](https://github.com/iMicknl))
- Implement the DataUpdateCoordinator [\#186](https://github.com/iMicknl/ha-tahoma/pull/186) ([tetienne](https://github.com/tetienne))
- Update implementation for Siren [\#183](https://github.com/iMicknl/ha-tahoma/pull/183) ([iMicknl](https://github.com/iMicknl))
- Add missing states for some sensor and binary sensor devices [\#182](https://github.com/iMicknl/ha-tahoma/pull/182) ([iMicknl](https://github.com/iMicknl))
- Add device attributes to attributes [\#180](https://github.com/iMicknl/ha-tahoma/pull/180) ([iMicknl](https://github.com/iMicknl))
- Add support for SwimmingPool devices [\#171](https://github.com/iMicknl/ha-tahoma/pull/171) ([iMicknl](https://github.com/iMicknl))
- Improve support for GasSensor, ThermalEnergySensor, WaterSensor and add support for Siren Status [\#170](https://github.com/iMicknl/ha-tahoma/pull/170) ([iMicknl](https://github.com/iMicknl))
- Simplify logic for RTS devices [\#169](https://github.com/iMicknl/ha-tahoma/pull/169) ([iMicknl](https://github.com/iMicknl))
- Add more ui\_classes and sort them alphabetically [\#168](https://github.com/iMicknl/ha-tahoma/pull/168) ([iMicknl](https://github.com/iMicknl))
- Make all functions async, utilise new Python wrapper, better exception handling, improved device mapping [\#160](https://github.com/iMicknl/ha-tahoma/pull/160) ([iMicknl](https://github.com/iMicknl))

🐛 **Bug Fixes**

- Error fetching TaHoma Event Fetcher data: Error communicating with the TaHoma API: None [\#191](https://github.com/iMicknl/ha-tahoma/issues/191)
- object of type 'States' has no len\(\) [\#175](https://github.com/iMicknl/ha-tahoma/issues/175)
- Tahoma installation fails login error [\#174](https://github.com/iMicknl/ha-tahoma/issues/174)
- cover/set\_cover\_position fails [\#173](https://github.com/iMicknl/ha-tahoma/issues/173)
- io:CyclicGarageOpenerIOComponent not accessible by services, automations, and has status unknown [\#146](https://github.com/iMicknl/ha-tahoma/issues/146)
-  io:VerticalExteriorAwningIOComponent shown as io:HorizontalAwningIOComponent [\#118](https://github.com/iMicknl/ha-tahoma/issues/118)
- io:HorizontalAwningIOComponent reports 0 as the current\_position when it's fully opened [\#103](https://github.com/iMicknl/ha-tahoma/issues/103)
- State not updated for Awning \(io:AwningReceiverUnoIOComponent\) [\#44](https://github.com/iMicknl/ha-tahoma/issues/44)
- State not updated for Gate \(io:DiscreteGateOpenerIOComponent\) [\#40](https://github.com/iMicknl/ha-tahoma/issues/40)
- Fix missing client for scene [\#196](https://github.com/iMicknl/ha-tahoma/pull/196) ([tetienne](https://github.com/tetienne))
- Rewrite climate component to async approach [\#187](https://github.com/iMicknl/ha-tahoma/pull/187) ([iMicknl](https://github.com/iMicknl))
- Fix cover implementation for devices with only cycle command [\#184](https://github.com/iMicknl/ha-tahoma/pull/184) ([iMicknl](https://github.com/iMicknl))
- Fix assumed state [\#178](https://github.com/iMicknl/ha-tahoma/pull/178) ([tetienne](https://github.com/tetienne))
- Fix how the unit of measurement is retrieved [\#177](https://github.com/iMicknl/ha-tahoma/pull/177) ([tetienne](https://github.com/tetienne))
- Fix execute\_command call [\#176](https://github.com/iMicknl/ha-tahoma/pull/176) ([tetienne](https://github.com/tetienne))
- Return unknown if position is over 100 [\#172](https://github.com/iMicknl/ha-tahoma/pull/172) ([iMicknl](https://github.com/iMicknl))

**Closed issues:**

- Add support for \[Opening dector\] \(io:SomfyContactIOSystemSensor\) [\#193](https://github.com/iMicknl/ha-tahoma/issues/193)
- Add support for AwningComponent \(io:HorizontalAwningIOComponent\) [\#59](https://github.com/iMicknl/ha-tahoma/issues/59)
- Add support for Siren \(io:SomfyIndoorSimpleSirenIOComponent\) [\#57](https://github.com/iMicknl/ha-tahoma/issues/57)
- Add support for ExteriorScreen \(rts:ExteriorBlindRTSComponent\) [\#43](https://github.com/iMicknl/ha-tahoma/issues/43)
- Add support for UpDownHorizontalAwning \(rts:HorizontalAwningRTSComponent\) [\#42](https://github.com/iMicknl/ha-tahoma/issues/42)
- Request support for Outdoor Siren \(rtd:OutdoorSirenRTDComponent\) [\#27](https://github.com/iMicknl/ha-tahoma/issues/27)
- Add support for Siren Status \(rtds:SirenStatusRTDSComponent\) [\#26](https://github.com/iMicknl/ha-tahoma/issues/26)
- Add support for Indoor Siren \(io:SomfyIndoorSimpleSirenIOComponent\) [\#25](https://github.com/iMicknl/ha-tahoma/issues/25)

## [v1.6.4](https://github.com/iMicknl/ha-tahoma/tree/v1.6.4) (2020-07-24)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v1.6.3...v1.6.4)

⚠️ **Breaking changes**

- Simplify climate integration [\#151](https://github.com/iMicknl/ha-tahoma/issues/151)
- Enhancement/refactor climate [\#159](https://github.com/iMicknl/ha-tahoma/pull/159) ([vlebourl](https://github.com/vlebourl))

✨ **Enhancement**

- Support for interior\_blind\_positionable\_stateful\_roof [\#149](https://github.com/iMicknl/ha-tahoma/issues/149)
- Remove \(or document\) offset for covers [\#112](https://github.com/iMicknl/ha-tahoma/issues/112)
- Remove return from `apply\_action` [\#154](https://github.com/iMicknl/ha-tahoma/pull/154) ([vlebourl](https://github.com/vlebourl))
- Add helper functions select\_command and select\_state [\#148](https://github.com/iMicknl/ha-tahoma/pull/148) ([vlebourl](https://github.com/vlebourl))
- Add cycle support for the cover platform [\#147](https://github.com/iMicknl/ha-tahoma/pull/147) ([tetienne](https://github.com/tetienne))
- Move forgotten icons to constants. [\#144](https://github.com/iMicknl/ha-tahoma/pull/144) ([vlebourl](https://github.com/vlebourl))
- Remove .format\(\). [\#143](https://github.com/iMicknl/ha-tahoma/pull/143) ([vlebourl](https://github.com/vlebourl))

📘 **Documentation**

- Update README.md with ExteriorHeatingSystem support. [\#166](https://github.com/iMicknl/ha-tahoma/pull/166) ([vlebourl](https://github.com/vlebourl))

🐛 **Bug Fixes**

- Sensors have too much precision. [\#163](https://github.com/iMicknl/ha-tahoma/issues/163)
- Cover fails to get current\_cover\_position for device 'rts:GenericRTSComponent'  [\#155](https://github.com/iMicknl/ha-tahoma/issues/155)
- Hcs PROBLEM [\#130](https://github.com/iMicknl/ha-tahoma/issues/130)
- Position is incorrectly inverted when 0 because bool\(0\) == False. [\#165](https://github.com/iMicknl/ha-tahoma/pull/165) ([vlebourl](https://github.com/vlebourl))
- Round float state to 2 digits. [\#164](https://github.com/iMicknl/ha-tahoma/pull/164) ([vlebourl](https://github.com/vlebourl))
- Fix rescheduling update. [\#158](https://github.com/iMicknl/ha-tahoma/pull/158) ([vlebourl](https://github.com/vlebourl))
- Return None when no position state [\#157](https://github.com/iMicknl/ha-tahoma/pull/157) ([tetienne](https://github.com/tetienne))
- Fix should\_wait return value [\#156](https://github.com/iMicknl/ha-tahoma/pull/156) ([vlebourl](https://github.com/vlebourl))
- Add support for 'screen' uiClass. [\#153](https://github.com/iMicknl/ha-tahoma/pull/153) ([vlebourl](https://github.com/vlebourl))

**Closed issues:**

- Add support for \[Somfy Terrace Heater\] \(io:SimpleExteriorHeatingIOComponent\) [\#161](https://github.com/iMicknl/ha-tahoma/issues/161)
- Refactor constants and strings [\#110](https://github.com/iMicknl/ha-tahoma/issues/110)

**Merged pull requests:**

- Remove all private properties [\#145](https://github.com/iMicknl/ha-tahoma/pull/145) ([tetienne](https://github.com/tetienne))

## [v1.6.3](https://github.com/iMicknl/ha-tahoma/tree/v1.6.3) (2020-07-09)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v1.6.2...v1.6.3)

🐛 **Bug Fixes**

- Fix command and state definitions being incorrectly set in the API [\#142](https://github.com/iMicknl/ha-tahoma/pull/142) ([vlebourl](https://github.com/vlebourl))

## [v1.6.2](https://github.com/iMicknl/ha-tahoma/tree/v1.6.2) (2020-07-09)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v1.6.1...v1.6.2)

🐛 **Bug Fixes**

- fix cover set up [\#138](https://github.com/iMicknl/ha-tahoma/pull/138) ([vlebourl](https://github.com/vlebourl))
- Fix lock set up [\#137](https://github.com/iMicknl/ha-tahoma/pull/137) ([vlebourl](https://github.com/vlebourl))

## [v1.6.1](https://github.com/iMicknl/ha-tahoma/tree/v1.6.1) (2020-07-09)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/v1.6...v1.6.1)

🐛 **Bug Fixes**

- Fix light update failing. [\#136](https://github.com/iMicknl/ha-tahoma/pull/136) ([vlebourl](https://github.com/vlebourl))

## [v1.6](https://github.com/iMicknl/ha-tahoma/tree/v1.6) (2020-07-09)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.5...v1.6)

⚠️ **Breaking changes**

- Remove obsolete YAML schema [\#120](https://github.com/iMicknl/ha-tahoma/pull/120) ([iMicknl](https://github.com/iMicknl))

✨ **Enhancement**

- Retrieve core:MeasuredValueType to understand if it is Celsius or Kelvin [\#111](https://github.com/iMicknl/ha-tahoma/issues/111)
- Add constants for all strings [\#126](https://github.com/iMicknl/ha-tahoma/pull/126) ([vlebourl](https://github.com/vlebourl))
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

- Fix release drafter [\#134](https://github.com/iMicknl/ha-tahoma/pull/134) ([vlebourl](https://github.com/vlebourl))
- Create CODEOWNERS [\#129](https://github.com/iMicknl/ha-tahoma/pull/129) ([tetienne](https://github.com/tetienne))
- Remove all self.\_\* variables in cover module [\#128](https://github.com/iMicknl/ha-tahoma/pull/128) ([tetienne](https://github.com/tetienne))
- Fixed a typo. [\#124](https://github.com/iMicknl/ha-tahoma/pull/124) ([vlebourl](https://github.com/vlebourl))
- Add an auto changelog issue [\#123](https://github.com/iMicknl/ha-tahoma/pull/123) ([vlebourl](https://github.com/vlebourl))
- Code readability improvements [\#121](https://github.com/iMicknl/ha-tahoma/pull/121) ([iMicknl](https://github.com/iMicknl))

## [1.5](https://github.com/iMicknl/ha-tahoma/tree/1.5) (2020-07-03)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.5-alpha2...1.5)

🐛 **Bug Fixes**

- custom\_components.tahoma.config\_flow - Unexpected exception - ValueError: No ui Class [\#99](https://github.com/iMicknl/ha-tahoma/issues/99)
- Update for light component \(rgb\) fails - error in logs [\#96](https://github.com/iMicknl/ha-tahoma/issues/96)
- Not authenticated error. [\#86](https://github.com/iMicknl/ha-tahoma/issues/86)
- Remove exception raising in Device `\_\_init\_\_` in the API [\#101](https://github.com/iMicknl/ha-tahoma/pull/101) ([vlebourl](https://github.com/vlebourl))
- Fix a test in api login. [\#100](https://github.com/iMicknl/ha-tahoma/pull/100) ([vlebourl](https://github.com/vlebourl))

## [1.5-alpha2](https://github.com/iMicknl/ha-tahoma/tree/1.5-alpha2) (2020-07-02)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.5-alpha1...1.5-alpha2)

🐛 **Bug Fixes**

- \[fix\] color\_RGB\_to\_hs is missing parameters [\#97](https://github.com/iMicknl/ha-tahoma/pull/97) ([vlebourl](https://github.com/vlebourl))
- Re-log in the API after a "error":"Not authenticated" [\#95](https://github.com/iMicknl/ha-tahoma/pull/95) ([vlebourl](https://github.com/vlebourl))

## [1.5-alpha1](https://github.com/iMicknl/ha-tahoma/tree/1.5-alpha1) (2020-07-02)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4.1...1.5-alpha1)

🐛 **Bug Fixes**

- Actions are applied sequentialy [\#92](https://github.com/iMicknl/ha-tahoma/issues/92)
- Covers move step by step and can't be stopped while moving [\#90](https://github.com/iMicknl/ha-tahoma/issues/90)
- Remove the lock on apply\_action [\#93](https://github.com/iMicknl/ha-tahoma/pull/93) ([vlebourl](https://github.com/vlebourl))

## [1.4.1](https://github.com/iMicknl/ha-tahoma/tree/1.4.1) (2020-07-01)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4...1.4.1)

✨ **Enhancement**

- Add climate platform [\#12](https://github.com/iMicknl/ha-tahoma/issues/12)
- Add active\_states to device\_state\_attributes [\#89](https://github.com/iMicknl/ha-tahoma/pull/89) ([vlebourl](https://github.com/vlebourl))

🐛 **Bug Fixes**

- fix api for missing states at login [\#94](https://github.com/iMicknl/ha-tahoma/pull/94) ([vlebourl](https://github.com/vlebourl))
- \[fix\] fix AttributeError: 'NoneType' object has no attribute 'state' … [\#87](https://github.com/iMicknl/ha-tahoma/pull/87) ([vlebourl](https://github.com/vlebourl))

## [1.4](https://github.com/iMicknl/ha-tahoma/tree/1.4) (2020-06-22)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4-alpha3...1.4)

✨ **Enhancement**

- Electricity Meter [\#80](https://github.com/iMicknl/ha-tahoma/issues/80)
- Add support for IO RGB Light \(io:DimmableRGBLightIOComponent\) [\#73](https://github.com/iMicknl/ha-tahoma/issues/73)
- Change Unsupported Tahoma device logging from `warning` to `debug` [\#32](https://github.com/iMicknl/ha-tahoma/issues/32)
- Adjust code style according to home-assistant/core [\#20](https://github.com/iMicknl/ha-tahoma/issues/20)
- \[feat\] Support io:TotalElectricalEnergyConsumptionIOSystemSensor [\#81](https://github.com/iMicknl/ha-tahoma/pull/81) ([vlebourl](https://github.com/vlebourl))
- Update cover & changelog [\#78](https://github.com/iMicknl/ha-tahoma/pull/78) ([iMicknl](https://github.com/iMicknl))
- Wait for apply\_action to finish before returning. [\#76](https://github.com/iMicknl/ha-tahoma/pull/76) ([vlebourl](https://github.com/vlebourl))
- Add support for "setRGB" command for light entity. [\#75](https://github.com/iMicknl/ha-tahoma/pull/75) ([vlebourl](https://github.com/vlebourl))
- Add climate entity for Somfy's Smart Thermostat [\#54](https://github.com/iMicknl/ha-tahoma/pull/54) ([vlebourl](https://github.com/vlebourl))

🐛 **Bug Fixes**

- Unable to change tilt position on io:BioclimaticPergolaIOComponent [\#74](https://github.com/iMicknl/ha-tahoma/issues/74)
- Add part of fix\_44 changes already [\#82](https://github.com/iMicknl/ha-tahoma/pull/82) ([iMicknl](https://github.com/iMicknl))
- Bugfix for unable to change tilt position on io:BioclimaticPergolaIOComponent \#74 [\#77](https://github.com/iMicknl/ha-tahoma/pull/77) ([iMicknl](https://github.com/iMicknl))

## [1.4-alpha3](https://github.com/iMicknl/ha-tahoma/tree/1.4-alpha3) (2020-06-18)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4-alpha2...1.4-alpha3)

🐛 **Bug Fixes**

- fixed a typo [\#72](https://github.com/iMicknl/ha-tahoma/pull/72) ([vlebourl](https://github.com/vlebourl))

## [1.4-alpha2](https://github.com/iMicknl/ha-tahoma/tree/1.4-alpha2) (2020-06-18)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.4-alpha1...1.4-alpha2)

✨ **Enhancement**

- Detected I/O inside the event loop. This is causing stability issues.  [\#2](https://github.com/iMicknl/ha-tahoma/issues/2)
- up/down as alternatives to open/close [\#71](https://github.com/iMicknl/ha-tahoma/pull/71) ([vlebourl](https://github.com/vlebourl))

## [1.4-alpha1](https://github.com/iMicknl/ha-tahoma/tree/1.4-alpha1) (2020-06-17)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.3...1.4-alpha1)

## [1.3](https://github.com/iMicknl/ha-tahoma/tree/1.3) (2020-06-17)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.2...1.3)

✨ **Enhancement**

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

📘 **Documentation**

- renamed tahoma or Tahoma to TaHoma. [\#46](https://github.com/iMicknl/ha-tahoma/pull/46) ([vlebourl](https://github.com/vlebourl))
- Add french translation [\#45](https://github.com/iMicknl/ha-tahoma/pull/45) ([vlebourl](https://github.com/vlebourl))

🐛 **Bug Fixes**

- Error unloading entry xxxxxx for tahoma [\#61](https://github.com/iMicknl/ha-tahoma/issues/61)
- Add support for Tahoma Scenes [\#47](https://github.com/iMicknl/ha-tahoma/issues/47)
- Fix \#61 [\#62](https://github.com/iMicknl/ha-tahoma/pull/62) ([vlebourl](https://github.com/vlebourl))
- Tahoma seems to not send all possible keys, depending on the devices … [\#52](https://github.com/iMicknl/ha-tahoma/pull/52) ([vlebourl](https://github.com/vlebourl))
- Fix domain [\#49](https://github.com/iMicknl/ha-tahoma/pull/49) ([iMicknl](https://github.com/iMicknl))

**Closed issues:**

- Add support for OccupancySensor \(io:SomfyOccupancyIOSystemSensor\) [\#19](https://github.com/iMicknl/ha-tahoma/issues/19)

**Merged pull requests:**

- fixes get\_events [\#55](https://github.com/iMicknl/ha-tahoma/pull/55) ([vlebourl](https://github.com/vlebourl))

## [1.2](https://github.com/iMicknl/ha-tahoma/tree/1.2) (2020-06-07)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.1...1.2)

✨ **Enhancement**

- Add better exception handling & retry logic for Tahoma API [\#4](https://github.com/iMicknl/ha-tahoma/issues/4)
- Refactored requests to avoid being locked out of the api. [\#24](https://github.com/iMicknl/ha-tahoma/pull/24) ([vlebourl](https://github.com/vlebourl))

📘 **Documentation**

- fixed a typo [\#38](https://github.com/iMicknl/ha-tahoma/pull/38) ([vlebourl](https://github.com/vlebourl))
- Rename to Somfy TaHoma [\#37](https://github.com/iMicknl/ha-tahoma/pull/37) ([iMicknl](https://github.com/iMicknl))
- Rename to Somfy TaHoma [\#36](https://github.com/iMicknl/ha-tahoma/pull/36) ([iMicknl](https://github.com/iMicknl))

🐛 **Bug Fixes**

- Position is not updated - PositionableHorizontalAwning - io:HorizontalAwningIOComponent [\#30](https://github.com/iMicknl/ha-tahoma/issues/30)
- ValueError: Config entry has already been setup! [\#16](https://github.com/iMicknl/ha-tahoma/issues/16)
- Reverse position for PositionableHorizontalAwning [\#41](https://github.com/iMicknl/ha-tahoma/pull/41) ([iMicknl](https://github.com/iMicknl))
- Fix ValueError: Config entry has already been setup! \#16 [\#35](https://github.com/iMicknl/ha-tahoma/pull/35) ([iMicknl](https://github.com/iMicknl))

**Closed issues:**

- Add support for Gate - DiscreteGateWithPedestrianPosition \(io:DiscreteGateOpenerIOComponent\) [\#18](https://github.com/iMicknl/ha-tahoma/issues/18)

## [1.1](https://github.com/iMicknl/ha-tahoma/tree/1.1) (2020-06-07)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.1-alpha2...1.1)

✨ **Enhancement**

- Refactor cover platform, removed hardcoded references [\#8](https://github.com/iMicknl/ha-tahoma/issues/8)

🐛 **Bug Fixes**

- `TahomaLight` object has no attribute `\_brightness` [\#22](https://github.com/iMicknl/ha-tahoma/issues/22)
- Fix faulty if statement [\#34](https://github.com/iMicknl/ha-tahoma/pull/34) ([iMicknl](https://github.com/iMicknl))
- Fix TahomaLight` object has no attribute `\_brightness [\#29](https://github.com/iMicknl/ha-tahoma/pull/29) ([iMicknl](https://github.com/iMicknl))

## [1.1-alpha2](https://github.com/iMicknl/ha-tahoma/tree/1.1-alpha2) (2020-06-05)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.1-alpha...1.1-alpha2)

✨ **Enhancement**

- Refactor cover platform [\#13](https://github.com/iMicknl/ha-tahoma/pull/13) ([iMicknl](https://github.com/iMicknl))

## [1.1-alpha](https://github.com/iMicknl/ha-tahoma/tree/1.1-alpha) (2020-06-04)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/1.0.0...1.1-alpha)

✨ **Enhancement**

- Add support for scenes [\#10](https://github.com/iMicknl/ha-tahoma/issues/10)
- Incorporate changes from tahoma\_extended [\#5](https://github.com/iMicknl/ha-tahoma/issues/5)
- Add occupancy sensor and start fixing async [\#15](https://github.com/iMicknl/ha-tahoma/pull/15) ([iMicknl](https://github.com/iMicknl))
- Add support for scenes [\#14](https://github.com/iMicknl/ha-tahoma/pull/14) ([iMicknl](https://github.com/iMicknl))

## [1.0.0](https://github.com/iMicknl/ha-tahoma/tree/1.0.0) (2020-06-04)

[Full Changelog](https://github.com/iMicknl/ha-tahoma/compare/014ff6a7acc5ca5a88cd78f695b7505ca2f01f1e...1.0.0)

✨ **Enhancement**

- Support Awning devices and update readme + changelog [\#11](https://github.com/iMicknl/ha-tahoma/pull/11) ([iMicknl](https://github.com/iMicknl))
- Apply fixes from tahoma\_extended & sensor/binary sensor improvements [\#7](https://github.com/iMicknl/ha-tahoma/pull/7) ([iMicknl](https://github.com/iMicknl))
- Add binary sensor and remove parts from normal sensor [\#6](https://github.com/iMicknl/ha-tahoma/pull/6) ([iMicknl](https://github.com/iMicknl))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
