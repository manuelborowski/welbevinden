from app import log
from app.data import settings as msettings, student as mstudent


def test_cron_task(opaque=None):
    if msettings.get_configuration_setting('test-prepare'):
        log.info('TEST: prepare for testing...')
        msettings.set_configuration_setting('test-prepare', False)
        all_students = mstudent.get_students()
        all_students.extend(mstudent.get_students(active=False))
        mstudent.delete_students(students=all_students)
        msettings.set_configuration_setting('sdh-prev-schoolyear', '')
        msettings.set_configuration_setting('sdh-current-schoolyear', '')
        msettings.set_configuration_setting('sdh-schoolyear-changed', False)
        msettings.set_configuration_setting('test-wisa-current-json', '')

