from app.data import settings as msettings, guest as mguest
from app import email, log, email_scheduler, flask_app
import datetime, time, re
from flask_mail import Message

def send_email(to, subject, content):
    sender = flask_app.config['MAIL_USERNAME']
    msg = Message(sender=sender, recipients=[to], subject=subject, html=content)
    try:
        email.send(msg)
        return True
    except Exception as e:
        log.error(f'send_email: ERROR, could not send email: {e}')
    return False

def send_register_ack(**kwargs):
    try:
        pass
        # reservation = mreservation.get_first_not_sent_registration()
        # if reservation:
        #     email_subject = msettings.get_configuration_setting('register-mail-ack-subject-template')
        #     email_content = msettings.get_configuration_setting('register-mail-ack-content-template')
        #     email_subject = email_subject.replace('{{TAG-PERIOD}}', reservation.period.period_string())
        #     email_content = email_content.replace('{{TAG-PERIOD}}', reservation.period.period_string())
        #     email_content = email_content.replace('{{TAG-NBR-BOXES}}', f'{reservation.reservation_nbr_boxes}')
        #     base_url = f'{msettings.get_configuration_setting("base-url")}/register?code={reservation.reservation_code}'
        #     url_template = f'<a href={base_url}>hier</a>'
        #     email_content = email_content.replace('{{TAG-UPDATE-URL}}', url_template)
        #
        #     info = reservation.flat(date_format='%d/%m/%Y %H:%M')
        #     info_string = '<br>U heeft volgende informatie ingegeven:<br>'
        #     info_string += '<table style="border:1px solid black;">'
        #     info_string += return_table_row('Naam school', info['name-school'])
        #     info_string += return_table_row('Leerkracht 1', info['name-teacher-1'])
        #     info_string += return_table_row('Leerkracht 2', info['name-teacher-2'])
        #     info_string += return_table_row('Leerkracht 3', info['name-teacher-3'])
        #     info_string += return_table_row('E-mailadres', info['email'])
        #     info_string += return_table_row('Telefoonnummer', info['phone'])
        #     info_string += return_table_row('Adres school', info['address'])
        #     info_string += return_table_row('Postcode', info['postal-code'])
        #     info_string += return_table_row('Gemeente', info['city'])
        #     info_string += return_table_row('Totaal aantal leerlingen', info['number-students'])
        #     info_string += '</table>'
        #
        #     if info['teams-meetings']:
        #         info_string += '<br><table style="border:1px solid black;">'
        #         info_string += return_table_row('Klasgroep', 'E-mail', 'Datum')
        #         for meeting in info['teams-meetings']:
        #             info_string += return_table_row(meeting['classgroup'], meeting['meeting-email'], meeting['meeting-date'])
        #         info_string += '</table>'
        #
        #     email_content = email_content.replace('{{TAG-RESERVATION-INFO}}', info_string)
        #     log.info(f'"{email_subject}" to {reservation.email}')
        #     ret = send_email(reservation.email, email_subject, email_content)
        #     if ret:
        #         reservation.set_ack_email_sent(True)
        #     return ret
        return False
    except Exception as e:
        log.error('Could not send e-mail: {e}')
    return False


def send_invite(**kwargs):
    try:
        if not msettings.get_configuration_setting('enable-send-invite-email'):
            return False
        guest = mguest.get_first_not_sent_invite()
        if not guest:
            return False
        email_send_max_retries = msettings.get_configuration_setting('email-send-max-retries')
        if guest.email_send_retry >= email_send_max_retries:
            guest.set_enabled(False)
            return False
        guest.set_email_send_retry(guest.email_send_retry + 1)

        email_subject = msettings.get_configuration_setting('invite-mail-subject-template')
        email_content = msettings.get_configuration_setting('invite-mail-content-template')

        url_tag = re.search('{{.*\|TAG_URL}}', email_content)
        url_text = url_tag.group(0).split('|')[0].split('{{')[1]
        url = f'{msettings.get_configuration_setting("base-url")}/register?code={guest.code}'
        url_template = f'<a href={url}>{url_text}</a>'
        email_content = re.sub('{{.*\|TAG_URL}}', url_template, email_content)
        log.info(f'"{email_subject}" to {guest.email}')
        ret = send_email(guest.email, email_subject, email_content)
        if ret:
            guest.set_ack_email_sent(True)
            return ret
        return False
    except Exception as e:
        log.error('Could not send e-mail: {e}')
    return False




send_email_config = [
    {'function': send_register_ack, 'args': {}},
    {'function': send_invite, 'args': {}},
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

