from app.data.models import Guest
from sqlalchemy import not_
from app import log, db
import sys


def add_guest(data):
    try:
        guest = Guest()
        for k, v in data.items():
            if hasattr(guest, k):
                if getattr(Guest, k).expression.type.python_type == type(v):
                    setattr(guest, k, v.strip() if isinstance(v, str) else v)
        db.session.add(guest)
        db.session.commit()
        return guest
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_guest_register_count(register_label, registration_date=None, indicator=None, status=None):
    try:
        q = Guest.query.filter(Guest.field_of_study.like(f'{register_label}%'))
        if registration_date:
            q = q.filter(Guest.register_timestamp <= registration_date)
        if indicator is not None:
            q = q.filter(Guest.indicator == indicator)
        if status is not None:
            q = q.filter(Guest.status == status)
        q = q.filter(Guest.enabled)
        guests_count = q.count()
        return guests_count
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return 0


def get_guest_register_last_timestamp(register_label, count, indicator=None):
    try:
        q = Guest.query.filter(Guest.field_of_study.like(f'{register_label}%'))
        q = q.filter(Guest.enabled)
        if indicator is not None:
            q = q.filter(Guest.indicator == indicator)
        q = q.slice(0, count)
        guest = q.all()
        return guest[-1] if guest else None
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_guests(data={}, special={}, order_by=None, first=False, count=False):
    try:
        q = Guest.query
        for k, v in data.items():
            if hasattr(Guest, k):
                q = q.filter(getattr(Guest, k) == v)
        for k, v in special.items():
            if k == 'register_timestamp_<=':
                q = q.filter(Guest.register_timestamp <= v)
            if k == 'field_of_study_like':
                q = q.filter(Guest.field_of_study.like(f'{v}%'))
        if order_by:
            q = q.order_by(getattr(Guest, order_by))
        if first:
            guest = q.first()
            return guest
        if count:
            return q.count()
        guests = q.all()
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


def get_guest_count(data={}):
    try:
        count = get_guests(data, count=True)
        return count
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return -1


def update_guest(guest, data={}):
    try:
        for k, v in data.items():
            if hasattr(guest, k):
                if getattr(Guest, k).expression.type.python_type == type(v):
                    setattr(guest, k, v.strip() if isinstance(v, str) else v)
        db.session.commit()
        return guest
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def delete_guest(codes=None):
    try:
        for code in codes:
            guest = get_first_guest({"code": code})
            db.session.delete(guest)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_not_sent_register_ack():
    try:
        guest = Guest.query.filter(Guest.enabled, not_(Guest.reg_ack_email_tx)).first()
        return guest
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_first_not_sent_timeslot_register_ack():
    try:
        guest = Guest.query.filter(Guest.enabled, not_(Guest.tsl_ack_email_tx)).first()
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
        query = query.filter(Guest.field_of_study.like(f"{reg}%"))
        if ind != 'N':
            query = query.filter(Guest.indicator == (ind == 'I'))

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
    search_constraints.append(Guest.last_name.like(search_string))
    search_constraints.append(Guest.first_name.like(search_string))
    search_constraints.append(Guest.note.like(search_string))
    search_constraints.append(Guest.email.like(search_string))
    search_constraints.append(Guest.phone.like(search_string))
    return search_constraints


