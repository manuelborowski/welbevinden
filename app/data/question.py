import sys
from app import log, db
from app.data import models as mmodels
from sqlalchemy_serializer import SerializerMixin


class Question(db.Model, SerializerMixin):
    __tablename__ = 'questions'

    date_format = '%d/%m/%Y'
    datetime_format = '%d/%m/%Y %H:%M'

    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(256), default='')
    label = db.Column(db.String(256), default='')
    type = db.Column(db.String(256), default='')
    seq = db.Column(db.Integer())


def commit():
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def add_question(data={}, commit=True):
    return mmodels.add_single(Question, data, commit)


def get_questions(data={}, fields=[], order_by=None, first=False, count=False, active=True):
    return mmodels.get_multiple(Question, data=data, fields=fields, order_by=order_by, first=first, count=count, active=active)


class QuestionCache:
    def __init__(self):
        self.__add_cache = {q.key + q.label + q.type: q for q in get_questions()}
        self.__key_cache = {q.key: q for q in get_questions()}
        self.__id_cache = {q.id: q for q in get_questions()}


    def add(self, question, period, targetgroep, label, question_type, seq):
        try:
            if question + period + targetgroep + label + question_type + str(seq) in self.__add_cache: #entry already exists
                return None

            if question + period + targetgroep in self.__key_cache:  # key already present, but seq, label or type has changed.  Replace
                oq = self.__key_cache[question + period + targetgroep]
                del(self.__add_cache[oq.key + oq.label + oq.type])
                oq.seq = seq
                oq.label = label
                oq.type = question_type
                commit()
                self.__add_cache[oq.key + label + question_type + str(seq)] = oq
                return oq

            new_question = add_question({"key": question + period + targetgroep, "label": label, "type": question_type, "seq": seq})
            self.__add_cache[question + period + targetgroep + label + question_type + str(seq)] = new_question
            self.__key_cache[question + period + targetgroep] = new_question
            self.__id_cache[new_question.id] = new_question
            return new_question
        except Exception as e:
            log.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise e

    def get_by_key(self, question, period, targetgroep):
        try:
            return self.__key_cache[question + period + targetgroep]
        except Exception as e:
            log.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise e

    def get_by_id(self, id):
        try:
            return self.__id_cache[id]
        except Exception as e:
            log.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise e

question_cache = QuestionCache()

