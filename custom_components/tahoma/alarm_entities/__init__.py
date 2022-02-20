"""Alarm Control Panel entities."""
from pyoverkiz.enums.ui import UIWidget

from .alarm_panel_controller import AlarmPanelController
from .stateful_alarm_controller import StatefulAlarmController
from .tsk_alarm_controller import TSKAlarmController

WIDGET_TO_ALARM_ENTITY = {
    UIWidget.TSKALARM_CONTROLLER: TSKAlarmController,
    UIWidget.STATEFUL_ALARM_CONTROLLER: StatefulAlarmController,
    UIWidget.ALARM_PANEL_CONTROLLER: AlarmPanelController,
}
