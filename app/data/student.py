import sys
from app import log, db
from app.data import models as mmodels
from sqlalchemy_serializer import SerializerMixin


class Student(db.Model, SerializerMixin):
    __tablename__ = 'students'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'

    id = db.Column(db.Integer(), primary_key=True)

    voornaam = db.Column(db.String(256), default='')
    naam = db.Column(db.String(256), default='')
    klas = db.Column(db.String(256), default='')
    schoolcode = db.Column(db.String(256), default='')
    schooljaar = db.Column(db.String(256), default='')


def commit():
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_student(data = {}, commit=True):
    return mmodels.add_single(Student, data, commit)


def add_students(data = []):
    return mmodels.add_multiple(Student, data)


