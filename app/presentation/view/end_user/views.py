from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context
import json
from . import end_user
from app import log, socketio
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from app.application import end_user as mend_user, info_items as minfo_items, floor as mfloor, visit as mvisit, \
    reservation as mreservation
import json


@end_user.route('/enter', methods=['POST', 'GET'])
def enter():
    try:
        code = request.args['code']
        visit = mend_user.get_visit(code, set_timestamp=True)
        clb_items = minfo_items.get_info_items('clb')
        flat_clb_items = [i.flat() for i in clb_items]
        config = {
            'intro_video': "https://www.youtube.com/embed/YrLk4vdY28Q",
        }
    except Exception as e:
        log.error(f'end user with args {request.args} could not enter: {e}')
        return render_template('end_user/error.html', error='could_not_enter')
    return render_template('end_user/end_user.html', user=visit.flat(), floors=mfloor.get_floors(),
                           config=config, async_mode=socketio.async_mode, items=flat_clb_items)


@end_user.route('/register', methods=['POST', 'GET'])
def register():
    try:
        available_periods = mreservation.get_available_periods()
        #
        #
        # register_for = request.args['for'] # guest, floor or fair
        # if register_for == mend_user.Profile.E_GUEST:
        #     timeslots = mvisit.get_timeslots()
        new_register_formio = dict(register_formio)
        update_available_periods(available_periods, new_register_formio, 'select-period-boxes')
        return render_template('end_user/register.html', registration_periods=available_periods,
                               registration_form=new_register_formio)
    except Exception as e:
        log.error(f'could not register {request.args}: {e}')
        return render_template('end_user/error.html', error='could_not_register', message=e)


@end_user.route('/register_save/<string:form_data>', methods=['POST', 'GET'])
def register_save(form_data):
    data = json.loads(form_data)
    periods = mreservation.get_available_periods()
    period_id = -1
    nbr_boxes = 0
    for period in periods:
        key = f'select-boxes-{period["id"]}'
        if (int(data[key]) > 0):
            period_id = period['id']
            nbr_boxes = int(data[key])
            break
    mreservation.add_registration(data['name-school'], data['name-teacher-1'], data['name-teacher-2'],
                                  data['name-teacher-3'], data['phone'], data['address'],
                                  data['postal-code'], data['city'], data['number-students'], period_id, nbr_boxes,
                                  data['meeting-email'], data['meeting-date'])


def update_available_periods(periods, form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            select_template = component['components'][0]
            data_template = component['components'][0]['data']['values'][0]
            component['components'] = []
            for period in periods:
                new = dict(select_template)
                new['data'] = dict({'values': []})
                for value in range(period['boxes_left'] + 1):
                    new_data = dict(data_template)
                    new_data['label'] = str(value)
                    new_data['value'] = str(value)
                    new['data']['values'].append(new_data)
                new['label'] = period['period']
                new['key'] = f'select-boxes-{period["id"]}'
                component['components'].append(new)
            return
        if 'components' in component:
            update_available_periods(periods, component, key)
    return


false = False
true = True
null = None

register_formio = \
    {
        "display": "form",
        "components": [
            {
                "html": "<p><i>Beste directie, beste meester/juf</i></p><p><i>Hieronder kan je een reservatie maken voor SUM-in-a-box.</i></p><p><i>Gelieve één tijdslot te kiezen en het aantal boxen te selecteren (1 box is geschikt voor maximum 25 leerlingen).</i></p><p><i>Vul de velden met de contactgegevens in, zodat we de box op het schooladres kunnen leveren en eventueel contact kunnen opnemen. Naar het mailadres zullen we ook een Microsoft Teams-link doorsturen.</i></p><p><i>Velden met een rood sterretje zijn verplicht.</i></p>",
                "label": "header",
                "refreshOnChange": false,
                "key": "header",
                "type": "content",
                "input": false,
                "tableView": false
            },
            {
                "title": "Contactgegevens",
                "theme": "warning",
                "collapsible": false,
                "key": "contact-info",
                "type": "panel",
                "label": "Contactgevevens",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Naam school",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "persistent": false,
                        "validate": {
                            "required": true
                        },
                        "key": "name-school",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "Voornaam en familienaam van leerkracht 1",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "validate": {
                            "required": true
                        },
                        "key": "name-teacher-1",
                        "type": "textfield",
                        "labelWidth": 40,
                        "labelMargin": 3,
                        "input": true
                    },
                    {
                        "label": "Voornaam en familienaam van leerkracht 2",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "persistent": false,
                        "key": "name-teacher-2",
                        "type": "textfield",
                        "labelWidth": 40,
                        "input": true
                    },
                    {
                        "label": "Voornaam en familienaam van leerkracht 3",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "persistent": false,
                        "key": "name-teacher-3",
                        "type": "textfield",
                        "labelWidth": 40,
                        "input": true
                    },
                    {
                        "label": "Telefoonnummer",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "key": "phone",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "Adres school (straat en nummer)",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "validate": {
                            "required": true
                        },
                        "key": "address",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "Postcode",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "validate": {
                            "required": true
                        },
                        "key": "postal-code",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "Gemeente",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "validate": {
                            "required": true
                        },
                        "key": "city",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "Totaal aantal leerlingen",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "validate": {
                            "required": true
                        },
                        "key": "number-students",
                        "type": "number",
                        "input": true
                    }
                ]
            },
            {
                "title": "Kies één datum en selecteer het aantal boxen",
                "theme": "warning",
                "collapsible": false,
                "key": "select-period-boxes",
                "type": "panel",
                "label": "Kies één datum en het aantal boxen (rechts)",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Datum-1",
                        "labelPosition": "left-left",
                        "widget": "choicesjs",
                        "tableView": true,
                        "defaultValue": "0",
                        "data": {
                            "values": [
                                {
                                    "label": "0",
                                    "value": "0"
                                },
                                {
                                    "label": "1",
                                    "value": "1"
                                }
                            ]
                        },
                        "dataType": "string",
                        "selectThreshold": 0.3,
                        "persistent": false,
                        "validate": {
                            "onlyAvailableItems": false
                        },
                        "key": "datum1",
                        "attributes": {
                            "class": "test"
                        },
                        "type": "select",
                        "indexeddb": {
                            "filter": {}
                        },
                        "input": true
                    }
                ]
            },
            {
                "title": "Op onderstaand mailadres sturen we een Microsoft Teams-link om digitaal vragen met de klasgroep te kunnen beantwoorden. Selecteer een datum en uur wanneer dit kan plaatsvinden:",
                "theme": "warning",
                "collapsible": false,
                "key": "info-or-questions",
                "type": "panel",
                "label": "Info of vragen?  Laat een e-mailadres achter en selecteer een datum en uur wanneer wij u kunnen contacteren",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "E-mailadres",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "key": "meeting-email",
                        "type": "email",
                        "input": true
                    },
                    {
                        "label": "Datum en uur in die uitgeleende week",
                        "labelPosition": "left-left",
                        "useLocaleSettings": true,
                        "allowInput": false,
                        "format": "dd/MM/yyyy HH:mm",
                        "tableView": false,
                        "enableMinDateInput": false,
                        "datePicker": {
                            "disableWeekends": false,
                            "disableWeekdays": false
                        },
                        "enableMaxDateInput": false,
                        "timePicker": {
                            "showMeridian": false
                        },
                        "persistent": false,
                        "key": "meeting-date",
                        "type": "datetime",
                        "input": true,
                        "widget": {
                            "type": "calendar",
                            "displayInTimezone": "viewer",
                            "locale": "en",
                            "useLocaleSettings": true,
                            "allowInput": false,
                            "mode": "single",
                            "enableTime": true,
                            "noCalendar": false,
                            "format": "dd/MM/yyyy HH:mm",
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
                ]
            },
            {
                "label": "Inzenden",
                "showValidations": false,
                "theme": "success",
                "size": "lg",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true
            }
        ]
    }
