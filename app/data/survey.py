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
    schoolcode = db.Column(db.String(256), default='')
    schooljaar = db.Column(db.Integer)
    survey = db.Column(MEDIUMTEXT)


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

