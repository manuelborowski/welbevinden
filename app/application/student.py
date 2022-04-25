from app import log
from app.data import student as mstudent
from app.application import formio as mformio
import sys

def add_student(data):
    try:
        data['s_date_of_birth'] = mformio.formiodate_to_date(data['s_date_of_birth'])
        data['i_intake_date'] = mformio.formiodate_to_date(data['i_intake_date'])
        student = mstudent.add_student(data)
        log.info(f"New registration: {student.s_last_name} {student.s_first_name}, {data}")
        return {"status": True, "data": {'s_code': student.s_code}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


############ student overview list #########
def format_data(db_list):
    out = []
    for student in db_list:
        em = student.to_dict()
        # student['row_action'] = student.id
        # student['DT_RowId']= student.id
        #
        # em = student.flat()
        #
        em.update({
            'row_action': student.id,
            'DT_RowId': student.id
        })
        out.append(em)
    return out

