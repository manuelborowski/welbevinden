from app import log
from app.data import student as mstudent, utils as mutils, school as mschool
import sys, base64


def delete_students(ids):
    mstudent.delete_students(ids)


def upload_studenten(students, school):
    try:
        current_year = mutils.get_current_schoolyear()
        log.info(f'{sys._getframe().f_code.co_name}: upload studenten for school {school} and schooljaar {current_year}')
        school_info = mschool.get_school_info_for_school(school)
        data = []
        for _, student in students.items():
            data.append({'voornaam': student['VOORNAAM'], 'naam': student["NAAM"], 'klas': student['KLAS'], 'schoolcode': school_info['schoolcode'], 'schooljaar': current_year})
        mstudent.add_students(data)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


############ datatables: student overview list #########
def format_data(db_list):
    out = []
    for student in db_list:
        em = student.to_dict()
        if student.foto_id == -1:
            em['overwrite_cell_color'] = [['foto', 'pink']]
        em.update({
            'row_action': student.id,
            'DT_RowId': student.id
        })
        out.append(em)
    return out


def get_nbr_photo_not_found():
    nbr_students_no_photo = mstudent.get_students({'foto_id': -1}, count=True)
    return nbr_students_no_photo