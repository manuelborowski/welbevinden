__all__ = ['tables', 'datatables', 'socketio', 'settings', 'warning', 'wisa', 'cron', 'cardpresso', 'photo', 'student', 'ad']

import app.application.socketio
import app.application.tables
import app.application.warning
import app.application.datatables
import app.application.settings
import app.application.photo
import app.application.wisa
import app.application.ad
import app.application.student
import app.application.cron
import app.application.cardpresso

cron.subscribe_cron_task(1, photo.photo_cron_task, None)
cron.subscribe_cron_task(2, wisa.wisa_cron_task, None)
cron.subscribe_cron_task(3, student.vsk_numbers_cron_task, None)
cron.subscribe_cron_task(4, cardpresso.new_badges_cron_task, None)
cron.subscribe_cron_task(5, cardpresso.new_rfid_to_database_cron_task, None)
cron.subscribe_cron_task(6, ad.ad_cron_task, None)

cron.subscribe_cron_task(8, student.deactivate_deleted_students_cron_task, None)
cron.subscribe_cron_task(9, student.clear_schoolyear_changed_flag_cron_task, None)
