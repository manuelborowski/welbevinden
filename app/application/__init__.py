__all__ = ['tables', 'datatables', 'socketio', 'settings', 'warning', 'wisa', 'cron', 'cardpresso', 'photo', 'student', 'ad', 'test', 'staff', 'school']

from . import school

from app.application.photo import photo_cron_task
from app.application.wisa import wisa_get_student_cron_task
from app.application.wisa import wisa_get_staff_cron_task
from app.application.cardpresso import new_badges_cron_task
from app.application.cardpresso import new_rfid_to_database_cron_task
from app.application.ad import cron_ad_student_task
from app.application.ad import cron_ad_get_student_computer_task
from app.application.staff import deactivate_deleted_staff_cron_task


# tag, cront-task, label, help

cron_table = [
]