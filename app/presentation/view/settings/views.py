import app.data.school
from . import settings
from flask import render_template, request
from flask_login import login_required, current_user
from app import log, instellen_required
from app.application import socketio as msocketio, student as mstudent
from app.application.util import deepcopy
from app.application import settings as msettings, formio as mformio
import json, sys, re, html, io



@settings.route('/settings', methods=['GET'])
@instellen_required
@login_required
def show():
    default_settings = msettings.get_default_values()
    formio_settings_copy = deepcopy(formio_settings)
    prepare_form(formio_settings_copy)
    data = {'default': default_settings, 'template': formio_settings_copy}
    return render_template('/settings/settings.html', data=data)


@settings.route('/settings/upload/<string:subject>/<string:school>', methods=['POST'])
@settings.route('/settings/upload/<string:subject>', methods=['POST'])
@settings.route('/settings/upload/', methods=['POST'])
@instellen_required
@login_required
def upload(subject=None, school=None):
    try:
        data_string = request.data.decode()
        lines = data_string.split()
        headers, data_string = lines[0].split(","), lines[1:]
        data = {j: {headers[i]: data_string[j].split(",")[i] for i in range(len(headers))} for j in range(len(data_string))}
        if subject == "leerlingenlijst":
            nbr_students = mstudent.upload_studenten(data, school)
        return json.dumps({"status": True, "data": f"Er zijn {nbr_students} studenten bewaard."})
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return json.dumps({"status": False, "data": html.escape(str(e))})


@settings.route('/settings/clear/<string:subject>/<string:school>', methods=['POST'])
@settings.route('/settings/clear/<string:subject>', methods=['POST'])
@settings.route('/settings/clear/', methods=['POST'])
@instellen_required
@login_required
def clear(subject=None, school=None):
    try:
        if subject == "leerlingenlijst":
            mstudent.clear_students(school)
        return json.dumps({"status": True, "data": f"De lijst met leerlingen is gewist."})
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        return json.dumps({"status": False, "data": html.escape(str(e))})




def update_settings_cb(msg, client_sid=None):
    try:
        data = msg['data']
        settings = json.loads(data['value'])
        msettings.set_setting_topic(settings)
        msocketio.broadcast_message({'type': 'settings', 'data': {'status': True}})
    except Exception as e:
        msocketio.broadcast_message({'type': 'settings', 'data': {'status': False, 'message': str(e)}})


msocketio.subscribe_on_type('settings', update_settings_cb)


def prepare_form(form):
    try:
        current_url = re.sub(f'{request.url_rule.rule}.*', '', request.url)
        school_infos = app.data.school.get_school_info_for_current_user()
        school_container = mformio.search_component(form, "container-scholen")
        data = []
        for key, info in school_infos.items():
            school_info = {"key": key,
                         "properties": [
                             {"key": "panel-school", "name": "title", "value": f"School: {info['label']}"},
                             {"key": "url-to-sept-ouders-survey", "name": "defaultValue", "value": f"{current_url}/survey/start/sept/ouders/{info['schoolcode']}"},
                             {"key": "url-to-sept-leerlingen-survey", "name": "defaultValue", "value": f"{current_url}/survey/start/sept/leerlingen/{info['schoolcode']}"},
                             {"key": "url-to-nov-ouders-survey", "name": "defaultValue", "value": f"{current_url}/survey/start/nov/ouders/{info['schoolcode']}"},
                             {"key": "url-to-nov-leerlingen-survey", "name": "defaultValue", "value": f"{current_url}/survey/start/nov/leerlingen/{info['schoolcode']}"},
                             {"key": "ouders-van", "name": "defaultValue", "value": info["venster-actief"]["ouders-van"]},
                             {"key": "ouders-tot", "name": "defaultValue", "value": info["venster-actief"]["ouders-tot"]},
                             {"key": "leerlingen-van", "name": "defaultValue", "value": info["venster-actief"]["leerlingen-van"]},
                             {"key": "leerlingen-tot", "name": "defaultValue", "value": info["venster-actief"]["leerlingen-tot"]},
                         ]}
            if info["type"] == "secundaireschool":
                school_info["properties"].append({"key": "klassen", "name": "defaultValue", "value": ", ".join(info["klassen"])})
                school_info["properties"].append({"key": "container-secundaire-school", "name": "hidden", "value": False})
                school_info["properties"].append({"key": "hidden-school-naam", "name": "defaultValue", "value": key})
                # input-file is a custom component and cannot emmit an event.  Therefore, in js, an eventhandler needs to be attached.  Therefore, the different input-file-components
                # need to have an unique id.  Same holds for the indicator
                school_info["properties"].append({"key": "input-file-select-leerlingen-lijst", "name": "attrs", "value": {"id" : f"{key}-input-file-select-leerlingen-lijst"}, })
                school_info["properties"].append({"key": "upload-leerlingen-lijst-indicator", "name": "key", "value": f"{key}-upload-leerlingen-lijst-indicator"})
            else:
                school_info["properties"].append({"key": "container-secundaire-school", "name": "hidden", "value": True})
            data.append(school_info)
        school_container["components"] = mformio.create_components(school_container["components"][0], data)
        if current_user.is_max_alle_scholen: # remove admin-only settings
            admin_container = mformio.search_component(form, "user-level-5")
            admin_container["components"] = []
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
formio_settings = \
    {
        "display": "form",
        "components": [
            {
                "label": "user-level-3",
                "tableView": false,
                "key": "user-level-3",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "label": "Container schoolinfo",
                        "tableView": false,
                        "key": "module-school-info",
                        "type": "container",
                        "input": true,
                        "components": [
                            {
                                "title": "Schoolinfo",
                                "theme": "success",
                                "collapsible": true,
                                "key": "panel-school-info",
                                "type": "panel",
                                "label": "Panel",
                                "collapsed": true,
                                "input": false,
                                "tableView": false,
                                "components": [
                                    {
                                        "label": "Container Scholen",
                                        "tableView": false,
                                        "key": "container-scholen",
                                        "type": "container",
                                        "input": true,
                                        "components": [
                                            {
                                                "label": "School",
                                                "tableView": false,
                                                "key": "container-school",
                                                "type": "container",
                                                "input": true,
                                                "components": [
                                                    {
                                                        "title": "School:",
                                                        "theme": "success",
                                                        "collapsible": true,
                                                        "key": "panel-school",
                                                        "type": "panel",
                                                        "label": "Panel",
                                                        "input": false,
                                                        "tableView": false,
                                                        "components": [
                                                            {
                                                                "title": "Link naar verschillende bevragingen",
                                                                "theme": "info",
                                                                "collapsible": true,
                                                                "key": "linkNaarVerschillendeBevragingen",
                                                                "type": "panel",
                                                                "label": "Panel",
                                                                "input": false,
                                                                "tableView": false,
                                                                "components": [
                                                                    {
                                                                        "label": "Columns",
                                                                        "columns": [
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Link naar SEPTEMBER ouders enquête",
                                                                                        "labelPosition": "left-left",
                                                                                        "disabled": true,
                                                                                        "tableView": true,
                                                                                        "defaultValue": "test",
                                                                                        "persistent": false,
                                                                                        "key": "url-to-sept-ouders-survey",
                                                                                        "type": "textfield",
                                                                                        "labelWidth": 25,
                                                                                        "input": true
                                                                                    }
                                                                                ],
                                                                                "width": 8,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 8
                                                                            },
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Kopieer naar clipboard",
                                                                                        "action": "event",
                                                                                        "showValidations": false,
                                                                                        "tableView": false,
                                                                                        "key": "copy-sept-ouders-user-link",
                                                                                        "type": "button",
                                                                                        "event": "copy-link-to-clipboard",
                                                                                        "input": true
                                                                                    }
                                                                                ],
                                                                                "width": 2,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 2
                                                                            }
                                                                        ],
                                                                        "key": "columns",
                                                                        "type": "columns",
                                                                        "input": false,
                                                                        "tableView": false
                                                                    },
                                                                    {
                                                                        "label": "Columns",
                                                                        "columns": [
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Link naar SEPTEMBER leerlingen enquête",
                                                                                        "labelPosition": "left-left",
                                                                                        "disabled": true,
                                                                                        "tableView": true,
                                                                                        "key": "url-to-sept-leerlingen-survey",
                                                                                        "type": "textfield",
                                                                                        "labelWidth": 25,
                                                                                        "input": true
                                                                                    }
                                                                                ],
                                                                                "width": 8,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 8
                                                                            },
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Kopieer naar clipboard",
                                                                                        "action": "event",
                                                                                        "showValidations": false,
                                                                                        "tableView": false,
                                                                                        "key": "copy-sept-leerlingen-user-link",
                                                                                        "type": "button",
                                                                                        "event": "copy-link-to-clipboard",
                                                                                        "input": true
                                                                                    }
                                                                                ],
                                                                                "width": 2,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 2
                                                                            }
                                                                        ],
                                                                        "key": "columns1",
                                                                        "type": "columns",
                                                                        "input": false,
                                                                        "tableView": false
                                                                    },
                                                                    {
                                                                        "label": "Columns",
                                                                        "columns": [
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Link naar NOVEMBER ouders enquête",
                                                                                        "labelPosition": "left-left",
                                                                                        "disabled": true,
                                                                                        "tableView": true,
                                                                                        "defaultValue": "test",
                                                                                        "persistent": false,
                                                                                        "key": "url-to-nov-ouders-survey",
                                                                                        "type": "textfield",
                                                                                        "labelWidth": 25,
                                                                                        "input": true
                                                                                    }
                                                                                ],
                                                                                "width": 8,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 8
                                                                            },
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Kopieer naar clipboard",
                                                                                        "action": "event",
                                                                                        "showValidations": false,
                                                                                        "tableView": false,
                                                                                        "key": "copy-nov-ouders-user-link",
                                                                                        "type": "button",
                                                                                        "event": "copy-link-to-clipboard",
                                                                                        "input": true
                                                                                    }
                                                                                ],
                                                                                "width": 2,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 2
                                                                            }
                                                                        ],
                                                                        "key": "columns2",
                                                                        "type": "columns",
                                                                        "input": false,
                                                                        "tableView": false
                                                                    },
                                                                    {
                                                                        "label": "Columns",
                                                                        "columns": [
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Link naar NOVEMBER leerlingen enquête",
                                                                                        "labelPosition": "left-left",
                                                                                        "disabled": true,
                                                                                        "tableView": true,
                                                                                        "key": "url-to-nov-leerlingen-survey",
                                                                                        "type": "textfield",
                                                                                        "labelWidth": 25,
                                                                                        "input": true
                                                                                    }
                                                                                ],
                                                                                "width": 8,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 8
                                                                            },
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Kopieer naar clipboard",
                                                                                        "action": "event",
                                                                                        "showValidations": false,
                                                                                        "tableView": false,
                                                                                        "key": "copy-nov-leerlingen-user-link",
                                                                                        "type": "button",
                                                                                        "event": "copy-link-to-clipboard",
                                                                                        "input": true
                                                                                    }
                                                                                ],
                                                                                "width": 2,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 2
                                                                            }
                                                                        ],
                                                                        "key": "columns3",
                                                                        "type": "columns",
                                                                        "input": false,
                                                                        "tableView": false
                                                                    }
                                                                ],
                                                                "collapsed": true
                                                            },
                                                            {
                                                                "title": "Wanneer is de bevraging actief",
                                                                "theme": "info",
                                                                "collapsible": true,
                                                                "key": "wanneerIsDeBevragingActief",
                                                                "type": "panel",
                                                                "label": "Panel",
                                                                "input": false,
                                                                "tableView": false,
                                                                "components": [
                                                                    {
                                                                        "label": "Columns",
                                                                        "columns": [
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Ouders bevraging, open van",
                                                                                        "labelPosition": "left-left",
                                                                                        "displayInTimezone": "utc",
                                                                                        "allowInput": false,
                                                                                        "format": "yyyy-MM-dd HH:mm",
                                                                                        "tableView": false,
                                                                                        "datePicker": {
                                                                                            "disableWeekends": false,
                                                                                            "disableWeekdays": false
                                                                                        },
                                                                                        "timePicker": {
                                                                                            "showMeridian": false
                                                                                        },
                                                                                        "enableMinDateInput": false,
                                                                                        "enableMaxDateInput": false,
                                                                                        "key": "ouders-van",
                                                                                        "type": "datetime",
                                                                                        "input": true,
                                                                                        "widget": {
                                                                                            "type": "calendar",
                                                                                            "displayInTimezone": "utc",
                                                                                            "locale": "en",
                                                                                            "useLocaleSettings": false,
                                                                                            "allowInput": false,
                                                                                            "mode": "single",
                                                                                            "enableTime": true,
                                                                                            "noCalendar": false,
                                                                                            "format": "yyyy-MM-dd HH:mm",
                                                                                            "hourIncrement": 1,
                                                                                            "minuteIncrement": 1,
                                                                                            "time_24hr": true,
                                                                                            "minDate": null,
                                                                                            "disableWeekends": false,
                                                                                            "disableWeekdays": false,
                                                                                            "maxDate": null
                                                                                        },
                                                                                        "labelWidth": 40
                                                                                    }
                                                                                ],
                                                                                "width": 4,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 4
                                                                            },
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "tot",
                                                                                        "labelPosition": "left-left",
                                                                                        "displayInTimezone": "utc",
                                                                                        "allowInput": false,
                                                                                        "format": "yyyy-MM-dd HH:mm",
                                                                                        "tableView": false,
                                                                                        "datePicker": {
                                                                                            "disableWeekends": false,
                                                                                            "disableWeekdays": false
                                                                                        },
                                                                                        "timePicker": {
                                                                                            "showMeridian": false
                                                                                        },
                                                                                        "enableMinDateInput": false,
                                                                                        "enableMaxDateInput": false,
                                                                                        "key": "ouders-tot",
                                                                                        "type": "datetime",
                                                                                        "input": true,
                                                                                        "widget": {
                                                                                            "type": "calendar",
                                                                                            "displayInTimezone": "utc",
                                                                                            "locale": "en",
                                                                                            "useLocaleSettings": false,
                                                                                            "allowInput": false,
                                                                                            "mode": "single",
                                                                                            "enableTime": true,
                                                                                            "noCalendar": false,
                                                                                            "format": "yyyy-MM-dd HH:mm",
                                                                                            "hourIncrement": 1,
                                                                                            "minuteIncrement": 1,
                                                                                            "time_24hr": true,
                                                                                            "minDate": null,
                                                                                            "disableWeekends": false,
                                                                                            "disableWeekdays": false,
                                                                                            "maxDate": null
                                                                                        },
                                                                                        "labelWidth": 10
                                                                                    }
                                                                                ],
                                                                                "width": 3,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 3
                                                                            }
                                                                        ],
                                                                        "key": "columns",
                                                                        "type": "columns",
                                                                        "input": false,
                                                                        "tableView": false
                                                                    },
                                                                    {
                                                                        "label": "Columns",
                                                                        "columns": [
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Leerlingen bevraging, open van",
                                                                                        "labelPosition": "left-left",
                                                                                        "displayInTimezone": "utc",
                                                                                        "allowInput": false,
                                                                                        "format": "yyyy-MM-dd HH:mm",
                                                                                        "tableView": false,
                                                                                        "datePicker": {
                                                                                            "disableWeekends": false,
                                                                                            "disableWeekdays": false
                                                                                        },
                                                                                        "timePicker": {
                                                                                            "showMeridian": false
                                                                                        },
                                                                                        "enableMinDateInput": false,
                                                                                        "enableMaxDateInput": false,
                                                                                        "key": "leerlingen-van",
                                                                                        "type": "datetime",
                                                                                        "input": true,
                                                                                        "widget": {
                                                                                            "type": "calendar",
                                                                                            "displayInTimezone": "utc",
                                                                                            "locale": "en",
                                                                                            "useLocaleSettings": false,
                                                                                            "allowInput": false,
                                                                                            "mode": "single",
                                                                                            "enableTime": true,
                                                                                            "noCalendar": false,
                                                                                            "format": "yyyy-MM-dd HH:mm",
                                                                                            "hourIncrement": 1,
                                                                                            "minuteIncrement": 1,
                                                                                            "time_24hr": true,
                                                                                            "minDate": null,
                                                                                            "disableWeekends": false,
                                                                                            "disableWeekdays": false,
                                                                                            "maxDate": null
                                                                                        },
                                                                                        "labelWidth": 40
                                                                                    }
                                                                                ],
                                                                                "width": 4,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 4
                                                                            },
                                                                            {
                                                                                "components": [
                                                                                    {
                                                                                        "label": "tot",
                                                                                        "labelPosition": "left-left",
                                                                                        "displayInTimezone": "utc",
                                                                                        "allowInput": false,
                                                                                        "format": "yyyy-MM-dd HH:mm",
                                                                                        "tableView": false,
                                                                                        "datePicker": {
                                                                                            "disableWeekends": false,
                                                                                            "disableWeekdays": false
                                                                                        },
                                                                                        "timePicker": {
                                                                                            "showMeridian": false
                                                                                        },
                                                                                        "enableMinDateInput": false,
                                                                                        "enableMaxDateInput": false,
                                                                                        "key": "leerlingen-tot",
                                                                                        "type": "datetime",
                                                                                        "input": true,
                                                                                        "widget": {
                                                                                            "type": "calendar",
                                                                                            "displayInTimezone": "utc",
                                                                                            "locale": "en",
                                                                                            "useLocaleSettings": false,
                                                                                            "allowInput": false,
                                                                                            "mode": "single",
                                                                                            "enableTime": true,
                                                                                            "noCalendar": false,
                                                                                            "format": "yyyy-MM-dd HH:mm",
                                                                                            "hourIncrement": 1,
                                                                                            "minuteIncrement": 1,
                                                                                            "time_24hr": true,
                                                                                            "minDate": null,
                                                                                            "disableWeekends": false,
                                                                                            "disableWeekdays": false,
                                                                                            "maxDate": null
                                                                                        },
                                                                                        "labelWidth": 10
                                                                                    }
                                                                                ],
                                                                                "width": 3,
                                                                                "offset": 0,
                                                                                "push": 0,
                                                                                "pull": 0,
                                                                                "size": "md",
                                                                                "currentWidth": 3
                                                                            }
                                                                        ],
                                                                        "key": "columns1",
                                                                        "type": "columns",
                                                                        "input": false,
                                                                        "tableView": false
                                                                    }
                                                                ],
                                                                "collapsed": true
                                                            },
                                                            {
                                                                "label": "Container secundaire school",
                                                                "tableView": false,
                                                                "key": "container-secundaire-school",
                                                                "type": "container",
                                                                "input": true,
                                                                "components": [
                                                                    {
                                                                        "label": "schoolnaam",
                                                                        "defaultValue": "test",
                                                                        "key": "hidden-school-naam",
                                                                        "type": "hidden",
                                                                        "input": true,
                                                                        "tableView": false
                                                                    },
                                                                    {
                                                                        "title": "Leerling gegevens",
                                                                        "theme": "info",
                                                                        "collapsible": true,
                                                                        "key": "leerlinggegevens",
                                                                        "type": "panel",
                                                                        "label": "Panel",
                                                                        "input": false,
                                                                        "tableView": false,
                                                                        "components": [
                                                                            {
                                                                                "html": "<p>In theorie zijn er 4 enquêtes per leerling (de leerling vult er één in september en één in december, en idem voor de ouders). &nbsp;Deze enquêtes zijn met elkaar gelinkt via de naam en klas van de leerling.<br>Wanneer de leerlingen en ouders de naam en klas zelf moeten opgeven, dan bestaat de kans dat (door een typfout) de enquête niet gelinkt kan worden.</p><p>Daarom kan de school een lijst van leerlingen uploaden, waaruit de ouders en leerling kunnen kiezen. &nbsp;Het is eventueel mogelijk om een bestaande lijst te verwijderen.</p><p>Als alternatief kan de school een lijst van klassen voorzien, zodat die consequent kan worden ingevoerd. &nbsp;Maak de lijst leeg indien dit niet gewenst wordt.</p><p>Als de leerlingenlijst en de klassenlijst niet gebruikt worden (leeg zijn), dan moeten ouders en leerling zelf naam, voornaam en klas opgeven.</p>",
                                                                                "label": "Content",
                                                                                "refreshOnChange": false,
                                                                                "key": "content",
                                                                                "type": "content",
                                                                                "input": false,
                                                                                "tableView": false
                                                                            },
                                                                            {
                                                                                "title": "Upload lijst van leerlingen",
                                                                                "theme": "info",
                                                                                "collapsible": false,
                                                                                "key": "klassenlijst",
                                                                                "type": "panel",
                                                                                "label": "Panel",
                                                                                "input": false,
                                                                                "tableView": false,
                                                                                "components": [
                                                                                    {
                                                                                        "html": "<p>Selecteer een csv bestand, waarin elke kolom een hoofding heeft.<br>Volgende kolommen <strong>moeten</strong> aanwezig zijn: NAAM, VOORNAAM, KLAS<br>Andere kolommen worden genegeerd.</p>",
                                                                                        "label": "Content",
                                                                                        "refreshOnChange": false,
                                                                                        "key": "content1",
                                                                                        "type": "content",
                                                                                        "input": false,
                                                                                        "tableView": false
                                                                                    },
                                                                                    {
                                                                                        "label": "HTML",
                                                                                        "tag": "input",
                                                                                        "attrs": [
                                                                                            {
                                                                                                "attr": "type",
                                                                                                "value": "file"
                                                                                            },
                                                                                            {
                                                                                                "attr": "accept",
                                                                                                "value": ".csv"
                                                                                            },
                                                                                            {
                                                                                                "attr": "style",
                                                                                                "value": "display:none"
                                                                                            }
                                                                                        ],
                                                                                        "refreshOnChange": false,
                                                                                        "customClass": "input-file-select-leerlingen-lijst",
                                                                                        "key": "input-file-select-leerlingen-lijst",
                                                                                        "properties": {
                                                                                            "onchange": "alert('test')"
                                                                                        },
                                                                                        "type": "htmlelement",
                                                                                        "input": false,
                                                                                        "tableView": false
                                                                                    },
                                                                                    {
                                                                                        "label": "Columns",
                                                                                        "columns": [
                                                                                            {
                                                                                                "components": [
                                                                                                    {
                                                                                                        "label": "Laad lijst",
                                                                                                        "action": "event",
                                                                                                        "showValidations": false,
                                                                                                        "tableView": false,
                                                                                                        "key": "laadLijst",
                                                                                                        "type": "button",
                                                                                                        "input": true,
                                                                                                        "event": "event-load-leerlingen-lijst"
                                                                                                    }
                                                                                                ],
                                                                                                "width": 1,
                                                                                                "offset": 0,
                                                                                                "push": 0,
                                                                                                "pull": 0,
                                                                                                "size": "md",
                                                                                                "currentWidth": 1
                                                                                            },
                                                                                            {
                                                                                                "components": [
                                                                                                    {
                                                                                                        "label": "Wis lijst",
                                                                                                        "action": "event",
                                                                                                        "showValidations": false,
                                                                                                        "theme": "warning",
                                                                                                        "tableView": false,
                                                                                                        "key": "wisLijst",
                                                                                                        "type": "button",
                                                                                                        "input": true,
                                                                                                        "event": "event-clear-leerlingen-lijst"
                                                                                                    }
                                                                                                ],
                                                                                                "size": "md",
                                                                                                "width": 1,
                                                                                                "offset": 0,
                                                                                                "push": 0,
                                                                                                "pull": 0,
                                                                                                "currentWidth": 1
                                                                                            },
                                                                                            {
                                                                                                "components": [
                                                                                                    {
                                                                                                        "label": "Text Field",
                                                                                                        "hideLabel": true,
                                                                                                        "disabled": true,
                                                                                                        "tableView": true,
                                                                                                        "defaultValue": "Nog geen lijst geladen",
                                                                                                        "key": "upload-leerlingen-lijst-indicator",
                                                                                                        "type": "textfield",
                                                                                                        "input": true
                                                                                                    }
                                                                                                ],
                                                                                                "width": 8,
                                                                                                "offset": 0,
                                                                                                "push": 0,
                                                                                                "pull": 0,
                                                                                                "size": "md",
                                                                                                "currentWidth": 8
                                                                                            }
                                                                                        ],
                                                                                        "key": "columns",
                                                                                        "type": "columns",
                                                                                        "input": false,
                                                                                        "tableView": false
                                                                                    }
                                                                                ]
                                                                            },
                                                                            {
                                                                                "title": "Klassenlijst",
                                                                                "theme": "info",
                                                                                "collapsible": false,
                                                                                "key": "klassenlijst1",
                                                                                "type": "panel",
                                                                                "label": "Panel",
                                                                                "input": false,
                                                                                "tableView": false,
                                                                                "components": [
                                                                                    {
                                                                                        "label": "Lijst van de klassen, gescheiden door een komma (bv 1A, 1B1, 1B2)",
                                                                                        "tableView": true,
                                                                                        "key": "klassen",
                                                                                        "type": "textfield",
                                                                                        "input": true
                                                                                    }
                                                                                ]
                                                                            }
                                                                        ],
                                                                        "collapsed": true
                                                                    }
                                                                ]
                                                            }
                                                        ],
                                                        "collapsed": true
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "label": "Opslaan",
                                        "showValidations": false,
                                        "theme": "warning",
                                        "tableView": false,
                                        "key": "submit",
                                        "type": "button",
                                        "saveOnEnter": false,
                                        "input": true
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "label": "user-level-5",
                "tableView": false,
                "key": "user-level-5",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "Templates",
                        "theme": "warning",
                        "collapsible": true,
                        "key": "templates",
                        "type": "panel",
                        "label": "Panel",
                        "collapsed": true,
                        "input": false,
                        "tableView": false,
                        "components": [
                            {
                                "label": "Gebruikers",
                                "tableView": false,
                                "key": "template-user",
                                "type": "container",
                                "input": true,
                                "components": [
                                    {
                                        "title": "Gebruikers",
                                        "theme": "warning",
                                        "collapsible": true,
                                        "key": "algemeen",
                                        "type": "panel",
                                        "label": "Algemeen",
                                        "collapsed": true,
                                        "input": false,
                                        "tableView": false,
                                        "components": [
                                            {
                                                "label": "Opslaan",
                                                "showValidations": false,
                                                "theme": "warning",
                                                "tableView": false,
                                                "key": "submit",
                                                "type": "button",
                                                "input": true,
                                                "saveOnEnter": false
                                            },
                                            {
                                                "label": "Detail template (formio)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "user-formio-template",
                                                "type": "textarea",
                                                "input": true
                                            },
                                            {
                                                "label": "Lijst template (JSON)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "user-datatables-template",
                                                "type": "textarea",
                                                "input": true
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "label": "enquete",
                                "tableView": false,
                                "key": "template-survey",
                                "type": "container",
                                "input": true,
                                "components": [
                                    {
                                        "title": "Enquête",
                                        "theme": "warning",
                                        "collapsible": true,
                                        "key": "RegistratieTemplate1",
                                        "type": "panel",
                                        "label": "Studenten",
                                        "collapsed": true,
                                        "input": false,
                                        "tableView": false,
                                        "components": [
                                            {
                                                "label": "Opslaan",
                                                "showValidations": false,
                                                "theme": "warning",
                                                "tableView": false,
                                                "key": "submit",
                                                "type": "button",
                                                "input": true,
                                                "saveOnEnter": false
                                            },
                                            {
                                                "label": "Enquête SEPTEMBER OUDERS template (formio)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "survey-sept-ouders-formio-template",
                                                "type": "textarea",
                                                "input": true
                                            },
                                            {
                                                "label": "Enquête SEPTEMBER LEERLINGEN template (formio)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "survey-sept-leerlingen-formio-template",
                                                "type": "textarea",
                                                "input": true
                                            },
                                            {
                                                "label": "Enquête NOVEMBER OUDERS template (formio)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "survey-nov-ouders-formio-template",
                                                "type": "textarea",
                                                "input": true
                                            },
                                            {
                                                "label": "Enquête NOVEMBER LEERLINGEN template (formio)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "survey-nov-leerlingen-formio-template",
                                                "type": "textarea",
                                                "input": true
                                            },
                                            {
                                                "label": "Enquête gedaan template (formio)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "survey-done-formio-template",
                                                "type": "textarea",
                                                "input": true
                                            },
                                            {
                                                "label": "Lijst overzicht-per-vraag template (JSON)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "opq-datatables-template",
                                                "type": "textarea",
                                                "input": true
                                            },
                                            {
                                                "label": "Lijst overzicht-per-leerling template (JSON)",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "ops-datatables-template",
                                                "type": "textarea",
                                                "input": true
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Modules",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "modules",
                        "type": "panel",
                        "label": "Panel",
                        "input": false,
                        "tableView": false,
                        "components": [
                            {
                                "label": "container-survey",
                                "tableView": false,
                                "key": "container-survey",
                                "type": "container",
                                "input": true,
                                "components": [
                                    {
                                        "title": "Enquête",
                                        "theme": "primary",
                                        "collapsible": true,
                                        "key": "enquete",
                                        "type": "panel",
                                        "label": "Panel",
                                        "input": false,
                                        "tableView": false,
                                        "components": [
                                            {
                                                "label": "Opslaan",
                                                "showValidations": false,
                                                "theme": "warning",
                                                "tableView": false,
                                                "key": "submit",
                                                "type": "button",
                                                "saveOnEnter": false,
                                                "input": true
                                            },
                                            {
                                                "label": "Minimum aantal dagen tussen twee enquêtes",
                                                "labelPosition": "left-left",
                                                "mask": false,
                                                "tableView": false,
                                                "delimiter": false,
                                                "requireDecimal": false,
                                                "inputFormat": "plain",
                                                "truncateMultipleSpaces": false,
                                                "key": "survey-minimum-delta-days",
                                                "type": "number",
                                                "input": true
                                            }
                                        ],
                                        "collapsed": false
                                    }
                                ]
                            },
                            {
                                "label": "scholen",
                                "tableView": false,
                                "key": "module-scholen",
                                "type": "container",
                                "input": true,
                                "components": [
                                    {
                                        "title": "Schoolprofielen",
                                        "theme": "primary",
                                        "collapsible": true,
                                        "key": "RegistratieTemplate1",
                                        "type": "panel",
                                        "label": "Studenten",
                                        "collapsed": true,
                                        "input": false,
                                        "tableView": false,
                                        "components": [
                                            {
                                                "label": "Opslaan",
                                                "showValidations": false,
                                                "theme": "warning",
                                                "tableView": false,
                                                "key": "submit",
                                                "type": "button",
                                                "input": true,
                                                "saveOnEnter": false
                                            },
                                            {
                                                "label": "Schoolprofielen",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "school-profile",
                                                "type": "textarea",
                                                "input": true
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "label": "API",
                                "tableView": false,
                                "key": "module-api",
                                "type": "container",
                                "input": true,
                                "components": [
                                    {
                                        "title": "API",
                                        "theme": "primary",
                                        "collapsible": true,
                                        "key": "api",
                                        "type": "panel",
                                        "label": "Cardpresso",
                                        "collapsed": true,
                                        "input": false,
                                        "tableView": false,
                                        "components": [
                                            {
                                                "label": "Opslaan ",
                                                "showValidations": false,
                                                "theme": "warning",
                                                "tableView": false,
                                                "key": "submit",
                                                "type": "button",
                                                "input": true
                                            },
                                            {
                                                "label": "API sleutels",
                                                "tooltip": "Een JSON lijst van sleutels",
                                                "autoExpand": false,
                                                "tableView": true,
                                                "key": "api-keys",
                                                "type": "textarea",
                                                "input": true
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        "collapsed": true
                    }
                ]
            }
        ]
    }
