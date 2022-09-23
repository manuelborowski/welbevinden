__all__ = ['tables', 'datatables', 'socketio', 'settings', 'warning', 'wisa', 'cron', 'cardpresso', 'photo', 'student', 'ad', 'test', 'staff']

import app.application.socketio
import app.application.tables
import app.application.warning
import app.application.datatables
import app.application.settings
import app.application.photo
import app.application.wisa
import app.application.ad
import app.application.student
import app.application.staff
import app.application.cron
import app.application.cardpresso
import app.application.test

cron.subscribe_cron_task(0, test.test_cron_task, None)
cron.subscribe_cron_task(1, photo.photo_cron_task, None)
cron.subscribe_cron_task(2, wisa.wisa_get_student_cron_task, None)
cron.subscribe_cron_task(3, wisa.wisa_get_staff_cron_task, None)
cron.subscribe_cron_task(4, student.vsk_numbers_cron_task, None)
cron.subscribe_cron_task(5, cardpresso.new_badges_cron_task, None)
cron.subscribe_cron_task(6, cardpresso.new_rfid_to_database_cron_task, None)
cron.subscribe_cron_task(7, ad.cron_ad_task, None)
cron.subscribe_cron_task(9, student.delete_marked_students_cron_task, None)
cron.subscribe_cron_task(10, staff.deactivate_deleted_staff_cron_task, None)
cron.subscribe_cron_task(11, student.clear_schoolyear_changed_flag_cron_task, None)
