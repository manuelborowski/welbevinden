from app import db, log
from app.data import models as mmodels
from sqlalchemy_serializer import SerializerMixin
import sys


class StringCache(db.Model, SerializerMixin):
    __tablename__ = 'string_cache'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'

    id = db.Column(db.Integer(), primary_key=True)
    label = db.Column(db.String(2048), default='')


def add_string(data={}, commit=True):
    return mmodels.add_single(StringCache, data, commit)


def get_strings(data={}, fields=[], order_by=None, first=False, count=False, active=True):
    return mmodels.get_multiple(StringCache, data=data, fields=fields, order_by=order_by, first=first, count=count, active=active)


class Strings:
    def __init__(self):
        self.__label_to_id_cache = {s.label: s.id for s in get_strings()}
        self.__id_to_label_cache = {s.id: s.label for s in get_strings()}

    def get_id(self, label):
        try:
            if label in self.__label_to_id_cache:
                return self.__label_to_id_cache[label]
            else:
                new_string = add_string({"label": label})
                self.__label_to_id_cache[label] = new_string.id
                self.__id_to_label_cache[new_string.id] = label
                return new_string.id
        except Exception as e:
            log.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise e

    def get_label(self, id):
        try:
            return self.__id_to_label_cache[id]
        except Exception as e:
            log.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise e


string_cache = Strings()


