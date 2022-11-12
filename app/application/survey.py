from app import log
from flask import make_response
from flask_login import current_user
from app.data import school as mschool
from app.application.util import deepcopy
from app.data.utils import get_current_schoolyear
from app.data.string_cache import string_cache
from app.data import student as mstudent, settings as msettings, survey as msurvey
from app.application import formio as mformio
import sys, json, datetime, csv
from io import StringIO


def delete_students(ids):
    mstudent.delete_students(ids)


def get_surveys(data={}, fields=[], order_by=None, first=False, count=False, active=True):
    return msurvey.get_surveys(data=data, fields=fields, order_by=order_by, first=first, count=count, active=active)


def get_schooljaren():
    try:
        surveys = msurvey.get_surveys()
        schooljaren = sorted(list(set([s.schooljaar for s in surveys])))
        return schooljaren
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def get_periodes():
    try:
        surveys = msurvey.get_surveys()
        periodes = sorted(list(set([s.period for s in surveys])))
        return periodes
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def get_targetgroups():
    try:
        surveys = msurvey.get_surveys()
        targetgroups = sorted(list(set([s.targetgroup for s in surveys])))
        return targetgroups
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def get_klassen(data={}):
    try:
        surveys = msurvey.get_surveys(data=data)
        klassen = sorted(list(set([s.klas for s in surveys])))
        if klassen[0] == "" and len(klassen) <= 1:
            return []
        return klassen
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def export_survey(filters):
    try:
        surveys = msurvey.get_filtered_surveys(filters)
        _, _, data_to_export = format_data_ops(surveys)
        if len(data_to_export) > 0:
            header = ["leerling", "klas", "school", "basisschool"]
            vragen = [v[0] for v in data_to_export[0]["row_detail"]["data"][1::]]
            header += vragen
            io_string = StringIO()
            csv_file = csv.DictWriter(io_string, fieldnames=header)
            body = []
            for student in data_to_export:
                item = {
                    "leerling": student["leerling"],
                    "klas": student["klas"],
                    "school": student["school"],
                    "basisschool": student["basisschool"],
                }
                item.update({i[0]: i[1] for i in student["row_detail"]["data"][1::]})
                body.append(item)
            csv_file.writeheader()
            csv_file.writerows(body)
            output = make_response(io_string.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename=overzicht-per-leerling.csv"
            output.headers["Content-type"] = "text/csv"
            return output
        return None
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


############## formio #########################


def update_form_cb(component, opaque):
    try:
        if component and "key" in component:
            if "clear-containers" in opaque and component["key"] in opaque["clear-containers"] and opaque["clear-containers"][component["key"]]:
                component["components"] = []
            elif "update-properties" in opaque and component["key"] in opaque["update-properties"]:
                for property in opaque["update-properties"][component["key"]]:
                    component[property["name"]] = property["value"]
            if "vraag-" in component["key"]:   #use the string cache to store strings or to get a reference to a stored string
                vraag_type = component["type"]
                if vraag_type == "textarea" and "vraag-hoort-bij-vorige" in component["key"]:
                    vraag_type = "textarea-hoort-bij-vorige"
                vraag_type_id = string_cache.get_id(vraag_type)
                vraag_id = string_cache.get_id(component["label"])
                if vraag_type in ["radio", "selectboxes"]:
                    for i, value in enumerate(component["values"]):
                        optie_id = string_cache.get_id(value["label"])
                        component["values"][i]["value"] = optie_id
                component["key"] = component["key"] + f"+{vraag_type_id}+{vraag_id}"
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_survey(period, targetgroup, schoolcode):
    def make_key(a, b, c):
        return (f"{a}+{b}+{c}")
    def unmake_key(k):
        return k.split("+")
    try:
        default = {}
        school_info = mschool.get_school_info_for_schoolcode(schoolcode)
        if not school_info or targetgroup not in ["ouders", "leerlingen"]:
            raise Exception("Sorry, er is een fout opgetreden")
        schooljaar = get_current_schoolyear()
        leerlingen = [[l.klas, l.naam, l.voornaam, 'not-found'] for l in mstudent.get_students({"schoolkey": school_info["key"], "schooljaar": schooljaar})]
        surveys = msurvey.get_surveys({"schoolkey": school_info["key"], "schooljaar": schooljaar})
        # extend with students from survey results, but only when leerlingen is not empty
        if leerlingen:
            survey_cache = {make_key(s.klas, s.naam, s.voornaam) : s.andereschool for s in surveys}
            for l in leerlingen:
                key = make_key(l[0], l[1], l[2])
                if key in survey_cache:
                    l[3]= survey_cache[key]
                    del(survey_cache[key])
            for key, basisschool in survey_cache.items():
                leerlingen.append(unmake_key(key) + [basisschool])
            select_leerling_data = {"values": [{"value": f"{klas}+{naam}+{voornaam}+{basisschool}", "label": f"{klas} {naam} {voornaam}"}
                                               for [klas, naam, voornaam, basisschool] in sorted(leerlingen, key=lambda i: i[0]+i[1]+i[2])]
                                              + [{"label": "Niet gevonden", "value": "not-found"}]}
        else:
            select_leerling_data = None
        select_klas_data = None
        if "klassen" in school_info and school_info["klassen"]:
            klassen = school_info["klassen"]
            select_klas_data = {"values": [{"value": k, "label": k} for k in klassen]}
        basisscholen = mschool.get_scholen_info_for_type("basisschool")
        extra_basisscholen = {s.andereschool: {"label": s.andereschool} for s in surveys if s.schoolkey not in basisscholen and s.andereschool not in basisscholen}
        basisscholen.update(extra_basisscholen)
        if basisscholen:
            select_basisschool_data = {"values": [{"value": k, "label": v["label"]} for (k, v) in sorted(basisscholen.items(), key=lambda i: i[0])] + [{"label": "Niet gevonden", "value": "not-found"}]}
        else:
            select_basisschool_data = None

        survey_template = deepcopy(msettings.get_configuration_setting(f"survey-{period}-{targetgroup}-formio-template"))
        template_update = {
            "clear-containers" : {
                "container-leerling-lijst": select_leerling_data == None,
                "container-klas": select_klas_data == None,
                "container-basisschool": True,
                "container-school-gegevens": not school_info["type"] == "secundaireschool",
                "container-secundaireschool": not school_info["type"] == "secundaireschool",
            },
            "update-properties": {
                "targetgroup-schoolcode": [{"name": "defaultValue", "value": f"{period}+{targetgroup}+{schoolcode}"}],
            },
        }

        if select_leerling_data:
            template_update["update-properties"]["select-leerling"] = [{"name": "data", "value": select_leerling_data}]
            template_update["update-properties"]["container-leerling-extra-gegevens"] = [{"name": "hidden", "value": True}]
        else:
             template_update["update-properties"]["container-leerling-extra-gegevens"] = [{"name": "conditional", "value": ""}]
        if select_klas_data:
            template_update["update-properties"]["select-klas"] = [{"name": "data", "value": select_klas_data}]
        if select_basisschool_data:
            template_update["update-properties"]["select-basisschool"] = [{"name": "data", "value": select_basisschool_data}]

        mformio.iterate_components_cb(survey_template, update_form_cb, template_update)
        return {'template': survey_template, "default": default}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def get_question_types_from_form_cb(component, opaque):
    try:
        if component and "key" in component:
            if "vraag-" == component["key"][:6]: # a component with a question must start with vraag-
                opaque[component["key"]] = component["type"]
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def save_survey(data):
    try:
        [period, targetgroup, schoolcode] = data["targetgroup-schoolcode"].split("+")
        school_info = mschool.get_school_info_for_schoolcode(schoolcode)
        container_leerlinggegevens = data["container-leerling-gegevens"]
        naam = voornaam = klas = ''
        basisschool = 'not-found'

        # only for secundaire school
        if "container-leerling-lijst" in container_leerlinggegevens and "select-leerling" in container_leerlinggegevens["container-leerling-lijst"]: # a leerlingenlijst dropdown is available
            selected_leerling = container_leerlinggegevens["container-leerling-lijst"]["select-leerling"]
            if selected_leerling != "not-found": # and contains a valid leerling
                [klas, naam, voornaam, basisschool] = selected_leerling.split("+")

        # no leerlingenlijst-dropdown is available or the leerling is not listed
        if "container-leerling-extra-gegevens" in container_leerlinggegevens:
            container_extra_leerling_gegevens = container_leerlinggegevens["container-leerling-extra-gegevens"]
            naam = container_extra_leerling_gegevens["achternaam"]
            voornaam = container_extra_leerling_gegevens["voornaam"]
            if "container-klas" in container_extra_leerling_gegevens and "select-klas" in container_extra_leerling_gegevens["container-klas"]:
                klas = container_extra_leerling_gegevens["container-klas"]["select-klas"]
            else:
                klas = ""
        if school_info["type"] == "secundaireschool":
            if basisschool == 'not-found':
                basisschool = container_leerlinggegevens["container-school-gegevens"]["container-secundaireschool"]["select-basisschool"]
                if basisschool == "not-found":
                    basisschool = container_leerlinggegevens["container-school-gegevens"]["container-secundaireschool"]["ss-andere-basisschool"]
        else:
            basisschool = school_info["key"]

        schooljaar = get_current_schoolyear()
        survey = []
        previous_surveys = msurvey.get_surveys({"naam": naam, "voornaam": voornaam, "klas": klas, "schoolkey": school_info["key"], "targetgroup": targetgroup,
                                               "schooljaar": schooljaar}, order_by="-timestamp")
        now = datetime.datetime.now()
        nbr_prvious_surveys = 0
        if previous_surveys: # check if a survey is sent in, too soon after a previous one.
            minimum_days = msettings.get_configuration_setting("survey-minimum-delta-days")
            for previous_survey in previous_surveys:
                delta_date = now - previous_survey.timestamp
                if delta_date.days < minimum_days:
                    nbr_prvious_surveys += 1
            if nbr_prvious_surveys >= 2 or nbr_prvious_surveys >= 1 and targetgroup == "leerlingen":
                return {"status": False, "message": f"U heeft al een enquête ingediend, deze enquête wordt genegeerd."}
        for (key, antwoord)  in data["container-vragen"].items():
            [vraag_type_id, vraag_id] = [int(v) for v in key.split("+")[1:]]
            vraag_type = string_cache.get_label(vraag_type_id)
            if vraag_type == "radio":
                if antwoord == '':
                    antwoord = string_cache.get_id("")
                survey.append((vraag_type_id, vraag_id, int(antwoord)))
            elif vraag_type == "selectboxes":
                selected_true = [int(k) for (k, v) in antwoord.items() if v]
                survey.append((vraag_type_id, vraag_id, selected_true))
            elif vraag_type == "textarea" or vraag_type == "textarea-hoort-bij-vorige":
                survey.append((vraag_type_id, vraag_id, antwoord))
        ret = msurvey.add_survey({"naam": naam, "voornaam": voornaam, "klas": klas, "targetgroup": targetgroup, "schoolkey": school_info["key"], "andereschool": basisschool,
                                  "schooljaar": schooljaar, "survey": json.dumps(survey), "timestamp": now, "period": period})
        data = {"targetgroup": targetgroup, "status": True, "message": ""}
        if ret == None:
            data["status"] = False
            data["message"] = "Er is een fout opgetreden en de enquête is niet bewaard.<br>Gelieve contact op te nemen met uw school"
        return data
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def form_data_get_school(school_type, base_container):
    if school_type == "secundaireschool":
        school = base_container["container-school-gegevens"]["container-secundaireschool"]["select-basisschool"]
        if school == "not-found":
            school = base_container["container-school-gegevens"]["container-secundaireschool"]["ss-andere-basisschool"]
    else:
        school = base_container["container-school-gegevens"]["container-basisschool"]["bs-welke-secundaire-school"]
    return school


def survey_done(data):
    try:
        survey_done_template = deepcopy(msettings.get_configuration_setting("survey-done-formio-template"))
        template_update = {
            "clear-containers": {
                "container-ouders": not data["targetgroup"] == "ouders",
                "container-leerlingen": not data["targetgroup"] == "leerlingen",
                "container-ok": not data["status"] == "true",
                "container-nok": not data["status"] == "false",
            },
            "update-properties": {
                "survey-response-text": [{"name": "html", "value": data["message"]}]
            },
        }
        mformio.iterate_components_cb(survey_done_template, update_form_cb, template_update)
        return {'template': survey_done_template}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e

############ datatables: survey overview list #########
def format_data_opq(db_list, total_count, filtered_count):
    out = []
    type_radio_id = string_cache.get_id("radio")
    type_selectboxes_id = string_cache.get_id("selectboxes")
    type_textarea_id = string_cache.get_id("textarea")
    type_textarea_hoort_bij_vorige_id = string_cache.get_id("textarea-hoort-bij-vorige")
    collect_data = {}
    remember_type_radio_answer = -1
    for item in db_list:
        survey = json.loads(item.survey)
        for question_nbr, [type_id, question_id, answer] in enumerate(survey):
            if question_id in collect_data:
                if type_id == type_radio_id:
                    if answer in collect_data[question_id][2]:
                        collect_data[question_id][2][answer] += 1
                    else:
                        collect_data[question_id][2][answer] = 1
                    collect_data[question_id][3] += 1
                    remember_type_radio_answer = answer
                elif type_id == type_selectboxes_id:
                    for a in answer:
                        if a in collect_data[question_id][2]:
                            collect_data[question_id][2][a] += 1
                        else:
                            collect_data[question_id][2][a] = 1
                    collect_data[question_id][3] += len(answer)
                elif type_id == type_textarea_id:
                    collect_data[question_id][2].append(answer)
                    collect_data[question_id][3] += 1
                elif type_id == type_textarea_hoort_bij_vorige_id:
                    collect_data[question_id][2].append([remember_type_radio_answer, answer])
                    collect_data[question_id][3] += 1
            else:
                if type_id == type_radio_id:
                    collect_data[question_id] = [type_id, question_nbr, {answer: 1}, 1]
                    remember_type_radio_answer = answer
                elif type_id == type_selectboxes_id:
                    collect_data[question_id] = [type_id, question_nbr, {a: 1 for a in answer}, len(answer)]
                elif type_id == type_textarea_id:
                    collect_data[question_id] = [type_id, question_nbr, [answer], 1]
                elif type_id == type_textarea_hoort_bij_vorige_id:
                    collect_data[question_id] = [type_id, question_nbr, [[remember_type_radio_answer, answer]], 1]
    for q, v in collect_data.items():
        details = {"width": 2, "data": [[f"Totaal: {v[3]} antwoorden", ""]]}
        if v[0] == type_radio_id or v[0] == type_selectboxes_id:
            for [item_id, nbr] in v[2].items():
                details["data"].append([string_cache.get_label(item_id), f"{nbr / v[3] * 100:.1f}%"])
        elif v[0] == type_textarea_id:
            for item in v[2]:
                details["data"].append([item, ""])
        elif v[0] == type_textarea_hoort_bij_vorige_id:
            sorted_list = sorted(v[2], key=lambda x: x[0])
            for [radio_answer, answer] in sorted_list:
                details["data"].append([f"({string_cache.get_label(radio_answer)}) {answer}", ""])
        out.append({
            "nummer": v[1],
            "vraag": string_cache.get_label(q),
            "row_detail": details,
            'DT_RowId': v[1]
        })
    return len(out), len(out), out


def format_data_ops(db_list, total_count=None, filtered_count=None):
    out = []
    type_radio_id = string_cache.get_id("radio")
    type_selectboxes_id = string_cache.get_id("selectboxes")
    show_name = current_user.is_at_least_naam_leerling
    school_cache = msettings.get_configuration_setting('school-profile')
    for i, item in enumerate(db_list):
        survey = json.loads(item.survey)
        details = {"width": 2, "data": [["Vraag", "Antwoord"]]}
        for question_nbr, [type_id, question_id, answer] in enumerate(survey):
            if type_id == type_selectboxes_id:
                answer_text = (", ").join([string_cache.get_label(a) for a in answer])
            elif type_id == type_radio_id:
                answer_text = string_cache.get_label(answer)
            else:
                answer_text = answer
            details["data"].append([string_cache.get_label(question_id), answer_text])
        out.append({
            "leerling": f"{item.naam} {item.voornaam}" if show_name else f"Leerling {i+1}",
            "klas": item.klas if show_name else "",
            "school": school_cache[item.schoolkey]["label"],
            "basisschool": school_cache[item.andereschool]["label"],
            "row_detail": details,
            'DT_RowId': item.id
        })
    return len(out), len(out), out


def post_sql_search_opq(l, search, count):
    out = []
    if search == "":
        return count, l
    for item in l:
        if search in item["vraag"]:
            out.append(item)
    return len(out), out


def post_sql_search_ops(l, search, count):
    out = []
    if search == "":
        return count, l
    for item in l:
        if search in item["leerling"] or search in item["klas"]:
            out.append(item)
    return len(out), out


def post_sql_order_ops(l, on, direction):
    out = sorted(l, key=lambda x: x[on], reverse=direction=="desc")
    return out
