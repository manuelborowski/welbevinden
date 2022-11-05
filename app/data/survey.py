import sys, json
from app import log, db
from app.data import models as mmodels
from sqlalchemy import text, func, desc
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


class StringCache(db.Model, SerializerMixin):
    __tablename__ = 'string_cache'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'

    id = db.Column(db.Integer(), primary_key=True)
    label = db.Column(db.String(2048), default='')


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


def add_string(data={}, commit=True):
    return mmodels.add_single(StringCache, data, commit)


def get_strings(data={}, fields=[], order_by=None, first=False, count=False, active=True):
    return mmodels.get_multiple(StringCache, data=data, fields=fields, order_by=order_by, first=first, count=count, active=active)


def add_default_string():
    s = get_strings({"label": ''})
    if not s:
        add_string({"label": ""})

add_default_string()

############ staff overview list #########
def pre_filter():
    return db.session.query(Survey)


def filter_data(query, filter):
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(Survey.naam.like(search_string))
    search_constraints.append(Survey.voornaam.like(search_string))
    return search_constraints

