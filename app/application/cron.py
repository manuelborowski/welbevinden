from app import ap_scheduler, log
from app.application import settings as msettings
import datetime, time
from apscheduler.triggers.cron import CronTrigger

CRON_TASK = 'datacollector-task'


def cron_task():
    for seq in sorted(cron_sub_tasks):
        cron_sub_tasks[seq]['cb'](cron_sub_tasks[seq]['opaque'])


def init_job(cron_template):
    try:
        running_job = ap_scheduler.get_job(CRON_TASK)
        if running_job:
            ap_scheduler.remove_job(CRON_TASK)
        if cron_template == 'now':
            ap_scheduler.add_job(CRON_TASK, cron_task, next_run_time=datetime.datetime.now())
        elif cron_template != '':
            ap_scheduler.add_job(CRON_TASK, cron_task, trigger=CronTrigger.from_crontab(cron_template))
    except Exception as e:
        log.error(f'could not init {CRON_TASK} job: {e}')


cron_sub_tasks = {}


def subscribe_cron_task(sequence_nbr, cb, opaque):
    cron_sub_tasks[sequence_nbr] = {
        'cb': cb,
        'opaque': opaque
    }


def update_cron_template(setting, value, opaque):
    try:
        if setting == 'cron-scheduler-template':
            init_job(value)
    except Exception as e:
        log.error(f'could not update cron-scheduler-template: {e}')
    return True

def start_job():
    try:
        cron_template = msettings.get_configuration_setting('cron-scheduler-template')
        if cron_template != 'now':  # prevent to run the cronjob each time the server is rebooted
            init_job(cron_template)
        msettings.subscribe_handle_update_setting('cron-scheduler-template', update_cron_template, None)
    except Exception as e:
        log.error(f'could not start cron-scheduler: {e}')


start_job()
