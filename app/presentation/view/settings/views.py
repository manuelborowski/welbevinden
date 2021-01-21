from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from .forms import AddForm, EditForm, ViewForm
from app import db, log, admin_required, data
from app.application import socketio as msocketio
from . import settings
from app.data.models import User

from app.presentation.layout import utils
from app.application import tables

from app.presentation.layout.utils import flash_plus, button_pressed

from app.application import settings as msettings

from app.presentation.view import base_multiple_items


# def formio_set_default_value(formio, default_values):
#     for component in formio["components"]:
#         formio_set_default_value(component, default_values)
#

@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    default_settings = msettings.get_configuration_settings()
    return render_template('/settings/settings.html',
                           settings_form=settings_formio, default_settings=default_settings)

def update_settings_cb(msg, client_sid=None):
    msettings.set_configuration_setting(msg['data']['setting'], msg['data']['value'])

msocketio.subscribe_on_type('settings', update_settings_cb)

from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
    {
        "display": "form",
        "components": [
            {
                "title": "Stage 2 configuratie",
                "theme": "primary",
                "collapsible": true,
                "key": "stage2Configuratie",
                "type": "panel",
                "label": "Stage 2 configuratie",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Wanneer wordt stage 2 actief?",
                        "optionsLabelPosition": "right",
                        "inline": false,
                        "tableView": false,
                        "defaultValue": "start-timeslot",
                        "values": [
                            {
                                "label": "Na start tijdslot",
                                "value": "start-timeslot",
                                "shortcut": ""
                            },
                            {
                                "label": "Na aanmelden",
                                "value": "logon",
                                "shortcut": ""
                            }
                        ],
                        "persistent": false,
                        "key": "stage-2-start-timer-at",
                        "type": "radio",
                        "input": true
                    },
                    {
                        "label": "Tijd begint te lopen na de start van het tijdslot",
                        "tableView": false,
                        "defaultValue": false,
                        "persistent": false,
                        "key": "stage-2-delay-start-timer-until-start-timeslot",
                        "conditional": {
                            "show": true,
                            "when": "stage-2-start-timer-at",
                            "eq": "logon"
                        },
                        "type": "checkbox",
                        "input": true
                    },
                    {
                        "label": "Tijd vooraleer stage 2 zichtbaar wordt (seconden)",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": false,
                        "tableView": false,
                        "defaultValue": 0,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "stage-2-delay",
                        "type": "number",
                        "input": true,
                        "labelWidth": 50
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Stage 3 configuratie",
                "theme": "primary",
                "collapsible": true,
                "key": "stage3Configuratie1",
                "type": "panel",
                "label": "Stage 3 configuratie",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Wanneer wordt stage 3 actief?",
                        "optionsLabelPosition": "right",
                        "inline": false,
                        "tableView": false,
                        "defaultValue": "start-timeslot",
                        "values": [
                            {
                                "label": "Na start tijdslot",
                                "value": "start-timeslot",
                                "shortcut": ""
                            },
                            {
                                "label": "Na aanmelden",
                                "value": "logon",
                                "shortcut": ""
                            }
                        ],
                        "persistent": false,
                        "key": "stage-3-start-timer-at",
                        "type": "radio",
                        "input": true
                    },
                    {
                        "label": "Tijd begint te lopen na de start van het tijdslot",
                        "tableView": false,
                        "defaultValue": false,
                        "persistent": false,
                        "key": "stage-3-delay-start-timer-until-start-timeslot",
                        "conditional": {
                            "show": true,
                            "when": "stage-3-start-timer-at",
                            "eq": "logon"
                        },
                        "type": "checkbox",
                        "input": true
                    },
                    {
                        "label": "Tijd vooraleer stage 3 zichtbaar wordt (seconden)",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": false,
                        "tableView": false,
                        "defaultValue": 0,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "stage-3-delay",
                        "type": "number",
                        "input": true,
                        "labelWidth": 50
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Tijdslot configuratie",
                "theme": "primary",
                "collapsible": true,
                "key": "tijdslotConfiguratie",
                "type": "panel",
                "label": "Tijdslot configuratie",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Eerste tijdslot start om",
                        "labelPosition": "left-left",
                        "useLocaleSettings": true,
                        "format": "yyyy-MM-dd HH:mm",
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
                        "key": "timeslot-first-start",
                        "type": "datetime",
                        "input": true,
                        "widget": {
                            "type": "calendar",
                            "displayInTimezone": "viewer",
                            "locale": "en",
                            "useLocaleSettings": true,
                            "allowInput": true,
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
                        }
                    },
                    {
                        "label": "Lengte van een tijdslot",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "timeslot-length",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Aantal tijdsloten",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "timeslot-number",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Aantal gasten per tijdslot",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "timeslot-max-guests",
                        "type": "number",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Registratie template en e-mail",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate",
                "type": "panel",
                "label": "Registratie template en e-mail",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Web registratie template",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "register-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-mail-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Registratie bevestigingse-mail: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "register-mail-ack-content-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "Teams-meeting bevestigingse-mail",
                "theme": "primary",
                "collapsible": true,
                "key": "teamsMeetingBevestigingseMail",
                "type": "panel",
                "label": "Panel",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Bevestigingse-mail: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "meeting-mail-ack-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Bevestigingse-mail: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "persistent": false,
                        "key": "meeting-mail-ack-content-template",
                        "type": "textarea",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "E-mail server settings",
                "theme": "primary",
                "collapsible": true,
                "key": "eMailServerSettings",
                "type": "panel",
                "label": "E-mail server settings",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Tijd (seconden) tussen het verzenden van e-mails",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "persistent": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "email-task-interval",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Max aantal e-mails per minuut",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": true,
                        "tableView": false,
                        "persistent": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "emails-per-minute",
                        "type": "number",
                        "input": true
                    },
                    {
                        "label": "Basis URL",
                        "labelPosition": "left-left",
                        "tableView": true,
                        "key": "base-url",
                        "type": "textfield",
                        "input": true
                    },
                    {
                        "label": "E-mails mogen worden verzonden",
                        "tableView": false,
                        "persistent": false,
                        "key": "enable-send-email",
                        "type": "checkbox",
                        "input": true,
                        "defaultValue": false
                    }
                ],
                "collapsed": true
            }
        ]
    }