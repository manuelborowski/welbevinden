from app.data import utils as mutils, guest as mguest
from app.application import event as mevent
import random, string, datetime
from app import log, db
import sys
from openpyxl import load_workbook
from io import BytesIO
from app.application import socketio as msocketio


def create_random_string(len=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(len))


def add_guest(full_name=None, first_name=None, last_name=None, email=None, code=None):
    try:
        guest = mguest.get_first_guest(email=email)
        if guest:
            return guest
        if not code:
            code = create_random_string(32)
        guest = mguest.add_guest(full_name, first_name, last_name, email, code)
        log.info(f'{sys._getframe().f_code.co_name}: {email}')
        return guest
    except Exception as e:
        mutils.raise_error(f'{sys._getframe().f_code.co_name}:', e)
    return None


def event_send_invite_emails(opaque):
    try:
        guests = mguest.get_guests(enabled=True)
        for guest in guests:
            guest.set_email_send_retry(0)
            guest.set_invite_email_sent(False)
    except Exception as e:
        mutils.raise_error(f'{sys._getframe().f_code.co_name}:', e)
    return None


mevent.subscribe_event('button-send-invite-emails', event_send_invite_emails, None)


def import_guest_info(file_storeage):
    try:
        guests = mguest.get_guests(enabled=True)
        guest_emails = [g.email for g in guests]
        guest_dict = XLSXDictReader(BytesIO(file_storeage.read()))
        for guest in guest_dict:
            if not guest['e-mailadres'] in guest_emails:
                code = create_random_string()
                phone = str(guest['telefoonnummer'])
                if phone[0] != '0':
                    phone = f'0{phone}'
                mguest.add_guest_bulk(full_name=guest['naam ouder'], phone=phone,
                                      email=guest['e-mailadres'], code=code)
                guest_emails.append(guest['e-mailadres'])
            if guest['e-mailadres begeleidende organisatie'] and not \
                    guest['e-mailadres begeleidende organisatie'] in guest_emails:
                phone = str(guest['telefoonnummer'])
                if phone[0] != '0':
                    phone = f'0{phone}'
                code = create_random_string()
                mguest.add_guest_bulk(full_name=guest['naam ouder'], phone=phone,
                                      email=guest['e-mailadres begeleidende organisatie'], code=code)
                guest_emails.append(guest['e-mailadres begeleidende organisatie'])
        mguest.add_guest_commit()
    except Exception as e:
        mutils.raise_error(f'{sys._getframe().f_code.co_name}:', e)
    return None


def XLSXDictReader(f):
    book = load_workbook(f)
    sheet = book.active
    rows = sheet.max_row
    cols = sheet.max_column
    headers = dict((i, sheet.cell(row=1, column=i).value) for i in range(1, cols))

    def item(i, j):
        return (sheet.cell(row=1, column=j).value, sheet.cell(row=i, column=j).value)

    return (dict(item(i, j) for j in range(1, cols + 1)) for i in range(2, rows + 1))

# add_guest('manuel', 'borowski', 'emmanuel.borowski@gmail.com')
# add_guest('manuel', 'campus', 'manuel.borowski@campussintursula.be')
