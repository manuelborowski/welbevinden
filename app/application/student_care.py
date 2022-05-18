from app import log
from app.data import student_care as mstudent_care
import app.data.settings
from app.application import formio as mformio
import sys, datetime

def add_student(data):
    try:
        data['s_date_of_birth'] = mformio.datestring_to_date(data['s_date_of_birth'])
        data['i_intake_date'] = mformio.datetimestring_to_datetime(data['i_intake_date'])
        student = mstudent_care.add_student(data)
        log.info(f"Add care: {student.s_last_name} {student.s_first_name}, {data}")
        return {"status": True, "data": {'id': student.id}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def update_student(data):
    try:
        student = mstudent_care.get_first_student({'id': data['id']})
        if student:
            del data['id']
            data['s_date_of_birth'] = mformio.datestring_to_date(data['s_date_of_birth'])
            data['i_intake_date'] = mformio.datetimestring_to_datetime(data['i_intake_date'])
            student = mstudent_care.update_student(student, data)
            if student:
                log.info(f"Update care: {student.s_last_name} {student.s_first_name}, {data}")
                return {"status": True, "data": {'id': student.id}}
        return {"status": False, "data": "Er is iets fout gegaan"}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def delete_students(ids):
    mstudent_care.delete_students(ids)


############## formio forms #############
def prepare_add_form():
    try:
        template = app.data.settings.get_json_template('care-formio-template')
        now = datetime.datetime.now()
        return {'template': template,
                'defaults': {'i_intake_date': mformio.datetime_to_datetimestring(now)}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_edit_form(id, read_only=False, pdf=False):
    try:
        student = mstudent_care.get_first_student({"id": id})
        template = app.data.settings.get_json_template('care-formio-template')
        template = mformio.prepare_for_edit(template, student.to_dict(), pdf)
        return {'template': template,
                'defaults': student.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e




############ care overview list #########
def format_data(db_list):
    out = []
    for student in db_list:
        em = student.to_dict()
        em.update({
            'row_action': student.id,
            'DT_RowId': student.id
        })
        out.append(em)
    return out

