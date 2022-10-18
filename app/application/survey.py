from app import log
from app.data import school as mschool
from app.application.util import deepcopy
from app.data.utils import get_current_schoolyear
from app.data import student as mstudent, photo as mphoto, settings as msettings
from app.application import formio as mformio
import sys, base64


def delete_students(ids):
    mstudent.delete_students(ids)



############## formio #########################


def iterate_form_cb(component, opaque):
    try:
        if component and "key" in component:
            if component["key"] in opaque:
                for property in opaque[component["key"]]:
                    component[property["name"]] = property["value"]
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_survey(targetgroup, schoolcode):
    try:
        default = {}
        school_info = mschool.get_school_info_for_schoolcode(schoolcode)
        if not school_info or targetgroup not in ["ouders", "leerlingen"]:
            raise Exception("Sorry, er is een fout opgetreden")
        schooljaar = get_current_schoolyear()
        studenten = mstudent.get_students({"schoolcode": school_info["schoolcode"], "schooljaar": schooljaar})
        # extend with students from survey results
        klassen = school_info["klassen"]
        basisscholen = mschool.get_scholen_info_for_type("basisschool")
        survey_template = deepcopy(msettings.get_configuration_setting("survey-formio-template"))

        if studenten:
            select_leerling_data = {"values": [{"value": f"{s.klas}-{s.naam}-{s.voornaam}-{'school'}", "label": f"{s.klas} {s.naam} {s.voornaam}"} for s in studenten] + [{"label": "Niet gevonden", "value": "not-found"}]}
        else:
            select_leerling_data = None
        if klassen:
            select_klas_data = {"values": [{"value": k, "label": k} for k in klassen]}
        else:
            select_klas_data = None
        if basisscholen:
            select_basisschool_data = {"values": [{"value": k, "label": v["label"]} for (k, v) in basisscholen.items()] + [{"label": "Niet gevonden", "value": "not-found"}]}
        else:
            select_basisschool_data = None

        template_info = {
            "container-ouders": [{"name": "hidden", "value": not targetgroup == "ouders"}],
            "container-leerlingen": [{"name": "hidden", "value": not targetgroup == "leerlingen"}],
            "select-leerling": [{"name": "hidden", "value": select_leerling_data == None}],
            "container-leerling-extra-gegevens": [{"name": "hidden", "value": not select_leerling_data == None}],
            "container-klas": [{"name": "hidden", "value": select_klas_data == None}],
            "container-basisschool": [{"name": "hidden", "value": not school_info["type"] == "basisschool"}],
            "container-secundaireschool": [{"name": "hidden", "value": not school_info["type"] == "secundaireschool"}],
            "targetgroup-schoolcode": [{"name": "defaultValue", "value": f"{targetgroup}-{schoolcode}"}],
        }

        if select_leerling_data:
            template_info["select-leerling"].append({"name": "data", "value": select_leerling_data})
        if select_klas_data:
            template_info["select-klas"] = [{"name": "data", "value": select_klas_data}]
        if select_basisschool_data:
            template_info["select-basisschool"] = [{"name": "data", "value": select_basisschool_data}]

        mformio.iterate_components_cb(survey_template, iterate_form_cb, template_info)
        return {'template': survey_template, "default": default}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e



def save_survey(data):
    try:
        print(data)
        [targetgroup, schoolcode] = data["targetgroup-schoolcode"].split("-")
        targetgroup_container = f"container-{targetgroup}"
        container_leerlinggegevens = data["container-leerling-gegevens"][targetgroup_container]
        selected_leerling = container_leerlinggegevens["container-leerling-lijst"]["select-leerling"]
        if selected_leerling == "not-found":
            naam = container_leerlinggegevens["container-leerling-extra-gegevens"]["achternaam"]
            voornaam = container_leerlinggegevens["container-leerling-extra-gegevens"]["voornaam"]

            klas = container_leerlinggegevens["container-leerling-extra-gegevens"]["container-klas"]["select-klas"]
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


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