from app import log
from app.data import school as mschool
from app.application.util import deepcopy
from app.data.utils import get_current_schoolyear
from app.data import student as mstudent, photo as mphoto, settings as msettings, survey as msurvey
from app.application import formio as mformio
import sys, base64, json, datetime


def delete_students(ids):
    mstudent.delete_students(ids)



############## formio #########################


def update_form_cb(component, opaque):
    try:
        if component and "key" in component:
            if component["key"] in opaque:
                for property in opaque[component["key"]]:
                    component[property["name"]] = property["value"]
            if "container-vraag" in component["key"]:   #change, depending on the question type, the values of the answers (copy the labels of the leerlingen to the values)
                vraag_ouders = vraag_leerlingen = None
                for sub_component in component["components"]:
                    if sub_component["key"] == "container-ouders":
                        vraag_ouders = sub_component["components"][0]
                    if sub_component["key"] == "container-leerlingen":
                        vraag_leerlingen = sub_component["components"][0]
                if vraag_leerlingen and vraag_ouders:
                    vraag_type = vraag_leerlingen["type"]
                    if vraag_type in opaque["strings"]:
                        vraag_type_id = opaque["strings"][vraag_type]
                    else:
                        survey_string = msurvey.add_string({"label": vraag_type})
                        opaque["strings"][vraag_type] = survey_string.id
                        vraag_type_id = survey_string.id
                    vraag = vraag_leerlingen["label"]
                    if vraag in opaque["strings"]:
                        vraag_id = opaque["strings"][vraag]
                    else:
                        survey_string = msurvey.add_string({"label": vraag})
                        opaque["strings"][vraag] = survey_string.id
                        vraag_id = survey_string.id

                    if vraag_type in ["radio", "selectboxes"]:
                        for i, value in enumerate(vraag_leerlingen["values"]):
                            optie = value["label"]
                            if optie in opaque["strings"]:
                                optie_id = opaque["strings"][optie]
                            else:
                                option = msurvey.add_string({"label": optie})
                                opaque["strings"][optie] = option.id
                                optie_id = option.id
                            vraag_leerlingen["values"][i]["value"] = optie_id
                            vraag_ouders["values"][i]["value"] = optie_id

                    vraag_ouders["key"] = vraag_ouders["key"] + f"+{vraag_type_id}+{vraag_id}"
                    vraag_leerlingen["key"] = vraag_leerlingen["key"] + f"+{vraag_type_id}+{vraag_id}"
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_survey(targetgroup, schoolcode):
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
        # extend with students from survey results
        surveys = msurvey.get_surveys({"schoolkey": school_info["key"], "schooljaar": schooljaar})
        survey_cache = {make_key(s.klas, s.naam, s.voornaam) : s.andereschool for s in surveys}
        string_cache = {s.label: s.id for s in msurvey.get_strings()}
        for l in leerlingen:
            key = make_key(l[0], l[1], l[2])
            if key in survey_cache:
                l[3]= survey_cache[key]
                del(survey_cache[key])
        for key, school in survey_cache.items():
            leerlingen.append(unmake_key(key) + [school])
        if leerlingen:
            select_leerling_data = {"values": [{"value": f"{klas}+{naam}+{voornaam}+{school}", "label": f"{klas} {naam} {voornaam}"}
                                               for [klas, naam, voornaam, school] in sorted(leerlingen, key=lambda i: i[0]+i[1]+i[2])]
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

        survey_template = deepcopy(msettings.get_configuration_setting("survey-formio-template"))
        template_update = {
            "container-ouders": [{"name": "hidden", "value": not targetgroup == "ouders"}],
            "container-leerlingen": [{"name": "hidden", "value": not targetgroup == "leerlingen"}],
            "container-leerling-lijst": [{"name": "hidden", "value": select_leerling_data == None}],
            "container-klas": [{"name": "hidden", "value": select_klas_data == None}],
            "container-basisschool": [{"name": "hidden", "value": not school_info["type"] == "basisschool"}],
            "container-secundaireschool": [{"name": "hidden", "value": not school_info["type"] == "secundaireschool"}],
            "targetgroup-schoolcode": [{"name": "defaultValue", "value": f"{targetgroup}+{schoolcode}"}],
            "strings": string_cache
        }

        if select_leerling_data:
            template_update["select-leerling"] = [{"name": "data", "value": select_leerling_data}]
            template_update["container-leerling-extra-gegevens"] = [{"name": "hidden", "value": True}]
        else:
             template_update["container-leerling-extra-gegevens"] = [{"name": "hidden", "value": False}, {"name": "conditional", "value": ""}]
        if select_klas_data:
            template_update["select-klas"] = [{"name": "data", "value": select_klas_data}]
        if select_basisschool_data:
            template_update["select-basisschool"] = [{"name": "data", "value": select_basisschool_data}]

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
        print(data)
        string_cache = {s.id: s.label for s in msurvey.get_strings()}
        empty_string_id = msurvey.get_strings({"label": ""}, first=True).id
        [targetgroup, schoolcode] = data["targetgroup-schoolcode"].split("+")
        school_info = mschool.get_school_info_for_schoolcode(schoolcode)
        container_leerlinggegevens = data["container-leerling-gegevens"][f"container-{targetgroup}"]
        naam = voornaam = klas = andere_school = ''

        if "container-leerling-lijst" in container_leerlinggegevens: # a leerlingenlijst dropdown is available
            selected_leerling = container_leerlinggegevens["container-leerling-lijst"]["select-leerling"]
            if selected_leerling != "not-found": # and contains a valid leerling
                [klas, naam, voornaam, andere_school] = selected_leerling.split("+")
                if andere_school == "not-found": # this is the first survey so no other-school has been selected yet
                    andere_school = form_data_get_school(school_info["type"], container_leerlinggegevens)
        # no leerlingenlijst-dropdown is available or the leerling is not listed
        if "container-leerling-extra-gegevens" in container_leerlinggegevens:
            container_extra_leerling_gegevens = container_leerlinggegevens["container-leerling-extra-gegevens"]
            naam = container_extra_leerling_gegevens["achternaam"]
            voornaam = container_extra_leerling_gegevens["voornaam"]
            if "container-klas" in container_extra_leerling_gegevens:
                klas = container_extra_leerling_gegevens["container-klas"]["select-klas"]
            else:
                klas = ""
            andere_school = form_data_get_school(school_info["type"], container_leerlinggegevens)

        schooljaar = get_current_schoolyear()
        survey = []
        previous_survey = msurvey.get_surveys({"naam": naam, "voornaam": voornaam, "klas": klas, "schoolkey": school_info["key"], "targetgroup": targetgroup,
                                               "schooljaar": schooljaar}, order_by="-timestamp", first=True)
        now = datetime.datetime.now()
        if previous_survey: # check if a survey is sent in, too soon after a previous one.
            minimum_days = msettings.get_configuration_setting("survey-minimum-delta-days")
            delta_date = now - previous_survey.timestamp
            if delta_date.days < minimum_days:
                return {"status": False, "message": f"U heeft al een enquête ingediend, deze enquête wordt genegeerd."}
        for container_vraag  in data["container-vragen"].values():
            container_targetgroup,  = container_vraag.values()
            (key, antwoord),  = container_targetgroup.items()
            [vraag_type_id, vraag_id] = [int(v) for v in key.split("+")[1:]]
            vraag_type = string_cache[vraag_type_id]
            if vraag_type == "radio":
                if antwoord == '':
                    antwoord = empty_string_id
                survey.append((vraag_type_id, vraag_id, int(antwoord)))
            elif vraag_type == "selectboxes":
                selected_true = [int(k) for (k, v) in antwoord.items() if v]
                survey.append((vraag_type_id, vraag_id, selected_true))
            elif vraag_type == "textarea":
                survey.append((vraag_type_id, vraag_id, antwoord))
        print(targetgroup, naam, voornaam, andere_school, survey)
        ret = msurvey.add_survey({"naam": naam, "voornaam": voornaam, "klas": klas, "targetgroup": targetgroup, "schoolkey": school_info["key"], "andereschool": andere_school,
                                  "schooljaar": schooljaar, "survey": json.dumps(survey), "timestamp": now})
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
            "container-ouders": [{"name": "hidden", "value": not data["targetgroup"] == "ouders"}],
            "container-leerlingen": [{"name": "hidden", "value": not data["targetgroup"] == "leerlingen"}],
            "container-ok": [{"name": "hidden", "value": not data["status"] == "true"}],
            "container-nok": [{"name": "hidden", "value": not data["status"] == "false"}],
            "survey-response-text": [{"name": "html", "value": data["message"]}]
        }
        mformio.iterate_components_cb(survey_done_template, update_form_cb, template_update)
        return {'template': survey_done_template}
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