import sys, json
from app import log, db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.mysql import MEDIUMBLOB


class Cardpresso(db.Model, SerializerMixin):
    __tablename__ = 'cardpresso'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'
    serialize_rules = ('-photo',)

    id = db.Column(db.Integer(), primary_key=True)

    voornaam = db.Column(db.String(256), default='')
    naam = db.Column(db.String(256), default='')
    leerlingnummer = db.Column(db.String(256), default='')
    klascode = db.Column(db.String(256), default='')
    middag = db.Column(db.String(256), default='')
    vsknummer = db.Column(db.String(256), default='')
    rfid = db.Column(db.String(256))
    geboortedatum = db.Column(db.String(256), default='')
    straat = db.Column(db.String(256), default='')
    huisnummer = db.Column(db.String(256), default='')
    busnummer = db.Column(db.String(256), default='')
    gemeente = db.Column(db.String(256), default='')
    photo = db.Column(MEDIUMBLOB)
    schoolnaam = db.Column(db.String(256), default='')
    schooljaar = db.Column(db.String(256), default='')

    new = db.Column(db.Boolean, default=True)
    delete = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    enable = db.Column(db.Boolean, default=True)
    changed = db.Column(db.TEXT, default='')


def get_columns():
    return [p for p in dir(Cardpresso) if not p.startswith('_')]


def add_student(data = {}, commit=True):
    try:
        student = Cardpresso()
        for k, v in data.items():
            if hasattr(student, k):
                if getattr(Cardpresso, k).expression.type.python_type == type(v):
                    setattr(student, k, v.strip() if isinstance(v, str) else v)
        db.session.add(student)
        if commit:
            db.session.commit()
        return student
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def add_students(data = []):
    try:
        for d in data:
            add_student(d, commit=False)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_student(student, data={}):
    try:
        for k, v in data.items():
            if hasattr(student, k):
                if getattr(Cardpresso, k).expression.type.python_type == type(v):
                    setattr(student, k, v.strip() if isinstance(v, str) else v)
        db.session.commit()
        return student
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def update_wisa_students(data = []):
    try:
        for d in data:
            student = d['student']
            for property in d['changed']:
                v = d[property]
                if hasattr(student, property):
                    if getattr(Cardpresso, property).expression.type.python_type == type(v):
                        setattr(student, property, v.strip() if isinstance(v, str) else v)
            student.changed = json.dumps(d['changed'])
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def flag_wisa_students(data = []):
    try:
        for d in data:
            student = d['student']
            student.new = d['new']
            student.changed = d['changed']
            student.delete = d['delete']
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None




def delete_students(ids=None):
    try:
        for id in ids:
            student = get_first_student({"id": id})
            db.session.delete(student)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None


def get_students(data={}, special={}, order_by=None, first=False, count=False):
    try:
        q = Cardpresso.query
        for k, v in data.items():
            if hasattr(Cardpresso, k):
                q = q.filter(getattr(Cardpresso, k) == v)
        if order_by:
            q = q.order_by(getattr(Cardpresso, order_by))
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


def get_first_student(data={}):
    try:
        user = get_students(data, first=True)
        return user
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
    return None



############ student overview list #########
def pre_filter():
    return db.session.query(Cardpresso)


def filter_data(query, filter):
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(Cardpresso.naam.like(search_string))
    search_constraints.append(Cardpresso.voornaam.like(search_string))
    return search_constraints

