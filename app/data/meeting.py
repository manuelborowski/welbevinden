from app.data.models import AvailablePeriod, SchoolReservation, TeamsMeeting
from app.data import utils as mutils
from app import log, db
import datetime, random, string

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


