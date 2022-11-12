import sys
from app import log, db
from app.data import models as mmodels
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.mysql import MEDIUMTEXT


class Survey(db.Model, SerializerMixin):
    __tablename__ = 'surveys'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'

    id = db.Column(db.Integer(), primary_key=True)
    voornaam = db.Column(db.String(256), default='')
    naam = db.Column(db.String(256), default='')
    klas = db.Column(db.String(256), default='')
    schoolkey = db.Column(db.String(256), default='')
    andereschool = db.Column(db.String(256), default='')
    targetgroup = db.Column(db.String(256), default='')
    period = db.Column(db.String(256), default='')
    schooljaar = db.Column(db.String(256), default='')
    survey = db.Column(MEDIUMTEXT)
    timestamp = db.Column(db.DateTime)


def commit():
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_survey(data={}, commit=True):
    return mmodels.add_single(Survey, data, commit)


def get_surveys(data={}, fields=[], order_by=None, first=False, count=False, active=True):
    return mmodels.get_multiple(Survey, data=data, fields=fields, order_by=order_by, first=first, count=count, active=active)


############ survey overview list #########
def pre_sql_query_opq():
    return db.session.query(Survey)


def pre_sql_filter_opq(q, filter):
    for f in filter:
        if f["value"] != "all":
            if "schoolkey" == f["name"]:
                attribute = "andereschool" if "basisschool" in f["value"] else "schoolkey"
                value = f["value"].split("+")[1]
                q = q.filter(getattr(Survey, attribute) == value)
            else:
                if hasattr(Survey, f["name"]):
                    q = q.filter(getattr(Survey, f["name"]) == f["value"])
    return q


def get_filtered_surveys(filters):
    try:
        q = pre_sql_query_opq()
        q = pre_sql_filter_opq(q, filters)
        surveys = q.all()
        return surveys
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
