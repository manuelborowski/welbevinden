from app.data.models import AvailablePeriod, SchoolReservation, TeamsMeeting
from app.data import utils as mutils
from app import log, db
import datetime, random, string


def update_meeting_code_by_id(id, value):
    try:
        meeting = TeamsMeeting.query.get(id)
        meeting.teams_meeting_code = value
        db.session.commit()
        log.info(f'meeting code update {id} {value}')
        return meeting
    except Exception as e:
        mutils.raise_error(f'could not update meeting code {id} {value}', e)
    return None


def update_meeting_email_sent_by_id(id, value):
    try:
        meeting = TeamsMeeting.query.get(id)
        meeting.ack_email_sent = value
        db.session.commit()
        log.info(f'meeting email-sent update {id} {value}')
        return meeting
    except Exception as e:
        mutils.raise_error(f'could not update meeting email-sent {id} {value}', e)
    return None


def update_meeting_email_enable_by_id(id, value):
    try:
        meeting = TeamsMeeting.query.get(id)
        meeting.enabled = value
        db.session.commit()
        log.info(f'meeting enable email update {id} {value}')
        return meeting
    except Exception as e:
        mutils.raise_error(f'could not update meeting enable email {id} {value}', e)
    return None


def get_first_not_sent_meeting():
    meeting = TeamsMeeting.query.filter(TeamsMeeting.enabled, TeamsMeeting.teams_meeting_code != '')
    meeting = meeting.filter(TeamsMeeting.ack_email_sent == False)
    meeting = meeting.first()
    return meeting


def delete_meeting(id=None, list=None):
    try:
        if id: list=[id]
        for mid in list:
            meeting = TeamsMeeting.query.get(mid)
            db.session.delete(meeting)
        db.session.commit()
        return True
    except Exception as e:
        mutils.raise_error(f'could not delete meeting {id}', e)
    return False


def subscribe_ack_email_sent(cb, opaque):
    return TeamsMeeting.subscribe_ack_email_sent(cb, opaque)


def pre_filter():
    return db.session.query(TeamsMeeting).join(SchoolReservation)


def search_data(search_string):
    search_constraints = []
    search_constraints.append(TeamsMeeting.classgroup.like(search_string))
    return search_constraints


def format_data(db_list):
    out = []
    for i in db_list:
        em = i.ret_dict()
        em['row_action'] = f"{i.id}"
        out.append(em)
    return out


