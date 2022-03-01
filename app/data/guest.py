from app.data.models import Guest
from app.data import settings as msettings
from sqlalchemy import not_
from app import log, db
import sys, json


def add_guest_bulk(full_name=None, child_name=None, phone=None, email=None, code=None, misc_field=None):
    try:
        guest = Guest(full_name=full_name, child_name=child_name, phone=phone, email=email, code=code, misc_field=misc_field)
        db.session.add(guest)
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def guest_bulk_commit():
    try:
        db.session.commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_guest(data):
    try:
        guest = Guest()
        for k, v in data.items():
            if hasattr(guest, k):
                setattr(guest, k, v.strip() if isinstance(v, str) else v)
        db.session.add(guest)
        db.session.commit()
        # guest = add_guest_bulk(full_name=full_name, child_name=child_name, phone=phone, email=email, code=code, misc_field=misc_field)
        # guest_bulk_commit()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None
# def add_guest(full_name=None, child_name=None,phone=None, email=None, code=None, misc_field=None):
#     try:
#         guest = add_guest_bulk(full_name=full_name, child_name=child_name, phone=phone, email=email, code=code, misc_field=misc_field)
#         guest_bulk_commit()
#         return guest
#     except Exception as e:
#         log.error(f'{sys._getframe().f_code.co_name}: {e}')
#     return None


def get_guest_register_count(register_label, registration_date=None, indicator=None):
    try:
        q = Guest.query.filter(Guest.field_of_study.like(f'{register_label}%'))
        if registration_date:
            q = q.filter(Guest.register_timestamp <= registration_date)
        if indicator != None:
            q = q.filter(Guest.indicator == indicator)
        q = q.filter(Guest.enabled)
        guests_count = q.count()
        return guests_count
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return 0


def get_guests(data={}, timeslot_is_not_none=False, timeslot_is_none=False, first=False, count=False):
    try:
        guests = Guest.query
        for k, v in data.items():
            if hasattr(Guest, k):
                guests = guests.filter(getattr(Guest, k) == v)
        if timeslot_is_not_none:
            guests = guests.filter(Guest.timeslot != None)
        if timeslot_is_none:
            guests = guests.filter(Guest.timeslot == None)
        if first:
            guest = guests.first()
            return guest
        if count:
            return guests.count()
        guests = guests.all()
        return guests
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_guest(data={}):
    try:
        guest = get_guests(data, first=True)
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_guest_count(timeslot=None):
    try:
        count = get_guests(timeslot=timeslot, enabled=True, count=True)
        return count
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return -1


def update_guest(guest, data={}, full_name=None, child_name=None, phone=None, email=None, timeslot=None, note=None,
                 misc_field=None):
    try:
        for k, v in data.items():
            if hasattr(guest, k):
                setattr(guest, k, v.strip() if isinstance(v, str) else v)
        db.session.commit()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None

def update_guest_bulk(guest, full_name=None, child_name=None, phone=None, email=None, timeslot=None, note=None, misc_field=None):
    try:
        if full_name:
            guest.child_last_name = full_name
        if child_name:
            guest.child_first_name = child_name
        if phone:
            guest.phone = phone
        if email:
            guest.email = email
        if timeslot:
            guest.timeslot = timeslot
        if note is not None:
            guest.note = note
        if misc_field is not None:
            guest.misc_field = misc_field
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None

def delete_guest(codes=None):
    try:
        for code in codes:
            guest = get_first_guest({"code": code})
            db.session.delete(guest)
        db.session.commit()
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_timeslot(guest, timeslot):
    try:
        guest.timeslot = timeslot
        db.session.commit()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_not_sent_invite():
    try:
        guest = Guest.query.filter(Guest.enabled, not_(Guest.invite_email_tx)).first()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_not_sent_ack():
    try:
        guest = Guest.query.filter(Guest.enabled, not_(Guest.reg_ack_email_tx)).first()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_not_sent_cancel():
    try:
        guest = Guest.query.filter(Guest.enabled, not_(Guest.cancel_email_tx)).first()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def pre_filter():
    return db.session.query(Guest)


def filter_data(query, filter):
    if 'register' in filter and filter['register'] != 'default':
        [reg, ind] = filter['register'].split('-')
        query = query.filter(Guest.field_of_study.like(f"{reg}%")).filter(Guest.indicator == (ind == 'I'))

    if 'timeslot' in filter:
        select = filter['timeslot']
        if 'yes' == select:
            query = query.filter(Guest.timeslot != None)
        elif 'no' == select:
            query = query.filter(Guest.timeslot == None)
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(Guest.child_last_name.like(search_string))
    search_constraints.append(Guest.child_first_name.like(search_string))
    search_constraints.append(Guest.email.like(search_string))
    search_constraints.append(Guest.phone.like(search_string))
    search_constraints.append(Guest.misc_field.like(search_string))
    return search_constraints


def format_data(db_list):
    register_settings = json.loads(msettings.get_configuration_setting('register-register-settings'))
    out = []
    for i in db_list:
        em = i.flat()
        em.update({
            'row_action': i.code,
            'id': i.id,
            'DT_RowId': i.code
        })
        out.append(em)
        em['register'] = register_settings[em['register']]['label']
    return out


