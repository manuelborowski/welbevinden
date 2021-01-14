from app.data import settings as msettings, reservation as mreservation
from app import email, log, email_scheduler, flask_app
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime, time, re


def send_email(email_info):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = email_info['subject']
    msg['From'] = 'sum-in-a-box@campussintursula.be'
    msg['To'] = email_info['to']
    html = MIMEText(email_info['body'], 'html')
    msg.attach(html)
    try:
        email.sendmail(msg['From'], msg['To'], msg.as_string())
        return True
    except Exception as e:
        log.error(f'send_email: ERROR, could not send email: {e}')
    return False

# send_email(None, None)

def send_register_ack(**kwargs):
    reservation = mreservation.get_registration(email_sent=False)
    if reservation:
        email_subject = msettings.get_configuration_setting('register-mail-ack-subject-template')
        email_content = msettings.get_configuration_setting('register-mail-ack-content-template')
        email_subject = email_subject.replace('{{TAG-PERIOD}}', reservation.period.period_string())
        email_content = email_content.replace('{{TAG-PERIOD}}', reservation.period.period_string())
        email_content = email_content.replace('{{TAG-NBR-BOXES}}', f'{reservation.reservation_nbr_boxes}')
        base_url = f'{msettings.get_configuration_setting("base-url")}/register?code={reservation.reservation_code}'
        template = f'<a href={base_url}>hier</a>'
        email_content = email_content.replace('{{TAG-UPDATE-URL}}', template)

        email_info = {
            'body': email_content,
            'subject': email_subject,
            'to': reservation.email,
        }
        log.info(f'"{email_subject}" to {reservation.email}')
        ret = send_email(email_info)
        if ret:
            reservation.email_is_sent()
        return ret
    return False


send_email_config = [
    {'function': send_register_ack, 'args': {}},
]


run_email_task = True
def send_email_task():
    nbr_sent_per_minute = 0
    while run_email_task:
        with flask_app.app_context():
            at_least_one_email_sent = True
            start_time = datetime.datetime.now()
            job_interval = msettings.get_configuration_setting('email-task-interval')
            emails_per_minute = msettings.get_configuration_setting('emails-per-minute')
            while at_least_one_email_sent:
                at_least_one_email_sent = False
                for send_email in send_email_config:
                    if run_email_task and msettings.get_configuration_setting('enable-send-email'):
                        ret = send_email['function'](**send_email['args'])
                        if ret:
                            nbr_sent_per_minute += 1
                            now = datetime.datetime.now()
                            delta = now - start_time
                            if (nbr_sent_per_minute >= emails_per_minute) and (delta < datetime.timedelta(seconds=60)):
                                time_to_wait = 60 - delta.seconds + 1
                                log.info(f'send_email_task: have to wait for {time_to_wait} seconds')
                                time.sleep(time_to_wait)
                                nbr_sent_per_minute = 0
                                start_time = datetime.datetime.now()
                            at_least_one_email_sent = True
        if run_email_task:
                now = datetime.datetime.now()
                delta = now - start_time
                if delta < datetime.timedelta(seconds=job_interval):
                    time_to_wait = job_interval - delta.seconds
                    time.sleep(time_to_wait)


def set_base_url(url):
    msettings.set_configuration_setting('base-url', url)


def stop_send_email_task():
    global run_email_task
    run_email_task = False


def start_send_email_task():
    running_job = email_scheduler.get_job('send_email_task')
    if running_job:
        email_scheduler.remove_job('send_email_task')
    email_scheduler.add_job('send_email_task', send_email_task)

start_send_email_task()

