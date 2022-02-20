"""Alarm Control Panel entities."""
from pyoverkiz.enums.ui import UIWidget

from .tsk_alarm_controller import TSKAlarmController

WIDGET_TO_ALARM_ENTITY = {
    UIWidget.TSKALARM_CONTROLLER: TSKAlarmController,
}
