from app import log
from flask import make_response
from flask_login import current_user
from app.data import school as mschool
from app.application.util import deepcopy
from app.data.utils import get_current_schoolyear, get_test_bevragingen
from app.data.string_cache import string_cache
from app.data.question import question_cache
from app.data import student as mstudent, settings as msettings, survey as msurvey, school as mschool
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
        if surveys:
            klassen = sorted(list(set([s.klas for s in surveys])))
            if klassen[0] == "" and len(klassen) <= 1:
                return []
            return klassen
        return []
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def export_survey(filters):
    try:
        surveys = msurvey.get_filtered_surveys(filters)
        if len(surveys) > 0:
            header = ["leerling", "klas", "school", "basisschool"]
            io_string = StringIO()
            body = []
            show_name = current_user.is_at_least_naam_leerling
            school_cache = msettings.get_configuration_setting('school-profile')
            header_cache = {}
            for i, survey in enumerate(surveys):
                temp = []
                item = {
                    "leerling": f"{survey.naam} {survey.voornaam}" if show_name else f"Leerling {i + 1}",
                    "klas": survey.klas if show_name else "",
                    "school": school_cache[survey.schoolkey]["label"] if school_cache[survey.schoolkey]["type"] == "secundaireschool" else "",
                    "basisschool": school_cache[survey.andereschool]["label"] if survey.andereschool in school_cache else survey.andereschool
                }
                survey_data = json.loads(survey.survey)
                for [answer, sequence_nbr, label_id, vraag_type] in survey_data:
                    label = string_cache.get_label(label_id)
                    if type(answer) is dict:
                        answer = (", ").join(answer)
                    temp.append([sequence_nbr, label, answer])
                    if sequence_nbr not in header_cache:
                        header_cache[sequence_nbr] = label
                item.update({i[1]: i[2] for i in sorted(temp, key=lambda x: x[0])})
                body.append(item)

            header += [h[1] for h in sorted(header_cache.items())]
            csv_file = csv.DictWriter(io_string, fieldnames=header)
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
            if "vraag-" in component["key"]:
                vraag_type = component["type"]
                if vraag_type == "textarea" and "vraag-hoort-bij-vorige" in component["key"]:
                    vraag_type = "textarea-hoort-bij-vorige"
                question_cache.add(component["key"], opaque["period"], opaque["targetgroup"], component["label"], vraag_type, opaque["sequence_nbr"])
                opaque["sequence_nbr"] += 1
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
            select_basisschool_data = {"values": [{"value": k, "label": v["label"].replace("(B)", "").strip()} for (k, v) in sorted(basisscholen.items(), key=lambda i: i[0])] + [{"label": "andere basisschool", "value": "not-found"}]}
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
            "targetgroup": targetgroup,
            "period": period,
            "sequence_nbr": 0,
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
        now = datetime.datetime.now()
        [period, targetgroup, schoolcode] = data["targetgroup-schoolcode"].split("+")
        school_info = mschool.get_school_info_for_schoolcode(schoolcode)
        is_test_survey = get_test_bevragingen()
        #check if the window is still active
        survey_start_string = (":").join(school_info["venster-actief"][f"{targetgroup}-van"].split("+")[0].split(":")[:2])
        survey_end_string = (":").join(school_info["venster-actief"][f"{targetgroup}-tot"].split("+")[0].split(":")[:2])
        survey_start = datetime.datetime.strptime(survey_start_string, "%Y-%m-%dT%H:%M")
        survey_end = datetime.datetime.strptime(survey_end_string, "%Y-%m-%dT%H:%M")
        if (now < survey_start or now > survey_end) and not is_test_survey:
            return {"status": False, "message": f"Onze excuses, maar de bevraging is geopend van {survey_start.strftime('%d/%m/%Y %H.%M')} tot {survey_end.strftime('%d/%m/%Y %H.%M')}"}
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
            klas = ""

        schooljaar = get_current_schoolyear()
        survey = []
        if not is_test_survey and naam != "" and voornaam != "": # Ignore if the survey is anonymous
            survey_start_string = (":").join(school_info["venster-actief"][f"{targetgroup}-van"].split("+")[0].split(":")[:2])
            survey_start = datetime.datetime.strptime(survey_start_string, "%Y-%m-%dT%H:%M")
            previous_surveys = msurvey.get_surveys({"naam": naam, "voornaam": voornaam, "klas": klas, "schoolkey": school_info["key"], "targetgroup": targetgroup,
                                                   "schooljaar": schooljaar}, order_by="-timestamp")
            nbr_previous_surveys = 0
            if previous_surveys: # check if a survey is sent in, too soon after a previous one.
                for previous_survey in previous_surveys:
                    if previous_survey.timestamp > survey_start:
                        nbr_previous_surveys += 1
                if nbr_previous_surveys >= 2 or nbr_previous_surveys >= 1 and targetgroup == "leerlingen": # ouders can send in 2 surveys
                    return {"status": False, "message": f"Onze excuses, maar u heeft al een bevraging ingediend, deze bevraging wordt genegeerd."}
        for vraag, antwoord  in data["container-vragen"].items():
            question_obj = question_cache.get_by_key(vraag, period, targetgroup)
            vraag_type = question_obj.type
            label_id = string_cache.get_id(question_obj.label)
            if vraag_type == "radio":
                survey.append((antwoord, question_obj.seq, label_id, vraag_type))
            elif vraag_type == "selectboxes":
                selected_true = [k for (k, v) in antwoord.items() if v]
                survey.append((selected_true, question_obj.seq, label_id, vraag_type))
            elif vraag_type == "textarea" or vraag_type == "textarea-hoort-bij-vorige":
                survey.append((antwoord, question_obj.seq, label_id, vraag_type))
        ret = msurvey.add_survey({"naam": naam, "voornaam": voornaam, "klas": klas, "targetgroup": targetgroup, "schoolkey": school_info["key"], "andereschool": basisschool,
                                  "schooljaar": schooljaar, "survey": json.dumps(survey), "timestamp": now, "period": period})
        data = {"targetgroup": targetgroup, "period": period, "status": True, "message": ""}
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
    try:
        school_info = mschool.get_school_info_for_current_user()
        if len(school_info) == 1 and list(school_info.values())[0]["type"] == "basisschool":
            question_whitelist = msettings.get_configuration_setting("basisscholen-question-whitelist")
        else:
            question_whitelist = []
        out = []
        collect_data = {}
        remember_type_radio_answer = -1
        for item in db_list:
            survey = json.loads(item.survey)
            for [answer, sequence_nbr, label_id, vraag_type] in survey:
                label = string_cache.get_label(label_id)
                if question_whitelist and not label in question_whitelist:
                    continue
                if sequence_nbr in collect_data:
                    if vraag_type == "radio":
                        if answer in collect_data[sequence_nbr][2]:
                            collect_data[sequence_nbr][2][answer] += 1
                        else:
                            collect_data[sequence_nbr][2][answer] = 1
                        collect_data[sequence_nbr][3] += 1
                        remember_type_radio_answer = answer
                    elif vraag_type == "selectboxes":
                        for a in answer:
                            if a in collect_data[sequence_nbr][2]:
                                collect_data[sequence_nbr][2][a] += 1
                            else:
                                collect_data[sequence_nbr][2][a] = 1
                        collect_data[sequence_nbr][3] += len(answer)
                    elif vraag_type == "textarea":
                        collect_data[sequence_nbr][2].append(answer)
                        collect_data[sequence_nbr][3] += 1
                    elif vraag_type == "textarea-hoort-bij-vorige":
                        collect_data[sequence_nbr][2].append([remember_type_radio_answer, answer])
                        collect_data[sequence_nbr][3] += 1
                else:
                    if vraag_type == "radio":
                        collect_data[sequence_nbr] = [label, vraag_type, {answer: 1}, 1]
                        remember_type_radio_answer = answer
                    elif vraag_type == "selectboxes":
                        collect_data[sequence_nbr] = [label, vraag_type, {a: 1 for a in answer}, len(answer)]
                    elif vraag_type == "textarea":
                        collect_data[sequence_nbr] = [label, vraag_type, [answer], 1]
                    elif vraag_type == "textarea-hoort-bij-vorige":
                        collect_data[sequence_nbr] = [label, vraag_type, [[remember_type_radio_answer, answer]], 1]

        for sequence_nbr, info in dict(sorted(collect_data.items())).items():
            details = {"width": 2, "data": [[f"Totaal: {info[3]} antwoorden", ""]]}
            if info[1] == "radio" or info[1] == "selectboxes":
                for [item, nbr] in info[2].items():
                    details["data"].append([item, f"{nbr / info[3] * 100:.1f}%"])
            elif info[1] == "textarea":
                for item in info[2]:
                    details["data"].append([item, ""])
            elif info[1] == "textarea-hoort-bij-vorige":
                sorted_list = sorted(info[2], key=lambda x: x[0])
                for [radio_answer, answer] in sorted_list:
                    details["data"].append([f"({radio_answer}) {answer}", ""])
            out.append({
                "nummer": sequence_nbr,
                "vraag": info[0],
                "row_detail": details,
                'DT_RowId': sequence_nbr
            })
        return len(out), len(out), out
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def format_data_ops(db_list, total_count=None, filtered_count=None):
    try:
        school_info = mschool.get_school_info_for_current_user()
        if len(school_info) == 1 and list(school_info.values())[0]["type"] == "basisschool":
            question_whitelist = msettings.get_configuration_setting("basisscholen-question-whitelist")
        else:
            question_whitelist = []
        out = []
        show_name = current_user.is_at_least_naam_leerling
        school_cache = msettings.get_configuration_setting('school-profile')
        for i, item in enumerate(db_list):
            survey = json.loads(item.survey)
            details = {"width": 2, "data": [["Vraag", "Antwoord"]]}
            temp = []
            for [answer, sequence_nbr, label_id, vraag_type] in survey:
                label = string_cache.get_label(label_id)
                if question_whitelist and not label in question_whitelist:
                    continue
                if type(answer) is dict:
                    answer = (", ").join(answer)
                temp.append([sequence_nbr, label, answer])
            details["data"] = [[d[1], d[2]] for d in sorted(temp, key=lambda x: x[0])]
            out.append({
                "leerling": f"{item.naam} {item.voornaam}" if show_name else f"Leerling {i+1}",
                "klas": item.klas if show_name else "",
                "school": school_cache[item.schoolkey]["label"] if school_cache[item.schoolkey]["type"] == "secundaireschool" else "",
                "basisschool": school_cache[item.andereschool]["label"] if item.andereschool in school_cache else item.andereschool,
                "row_detail": details,
                'DT_RowId': item.id
            })
        return len(out), len(out), out
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


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
