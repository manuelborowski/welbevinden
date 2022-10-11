from app import log
from app.data import student as mstudent, settings as msettings, photo as mphoto
from app.application import formio as mformio
from app.application.settings import subscribe_update_container
import sys, base64


def delete_students(ids):
    mstudent.delete_students(ids)



def handle_school_settings(key, container, opaque):
    try:
        school_settings = msettings.get_configuration_setting('school-profile')
        scholen_container = container["container-scholen"]
        for school, settings in scholen_container.items():
            if school_settings[school]["type"] == "secundaireschool":
                school_settings[school]["klassen"] = settings["container-secundaire-school"]["klassen"].split(",")
        msettings.set_configuration_setting('school-profile', school_settings)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


subscribe_update_container('module-school-info', handle_school_settings, None)

############## formio #########################
def prepare_view_form(id, read_only=False):
    try:
        student = mstudent.get_first_student({"id": id})
        template = app.data.settings.get_configuration_setting('student-formio-template')
        photo = mphoto.get_first_photo({'filename': student.foto})
        data = {"photo": base64.b64encode(photo.photo).decode('utf-8') if photo else ''}
        template = mformio.prepare_for_edit(template, data)
        return {'template': template,
                'defaults': student.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


############ datatables: student overview list #########
def format_data(db_list):
    out = []
    for survey in db_list:
        em = survey.to_dict()
        em.update({
            'row_action': survey.id,
            'DT_RowId': survey.id
        })
        out.append(em)
    return out