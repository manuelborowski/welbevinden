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

false = False
true = True

@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    stage_settings = msettings.get_stage_settings()

    return render_template('/settings/settings.html', stage_settings_form=stage_settings_formio,
                           default_stage_settings=stage_settings)

def update_settings_cb(msg, client_sid=None):
    msettings.set_stage_setting(msg['data']['setting'], msg['data']['value'])

msocketio.subscribe_on_type('settings', update_settings_cb)


stage_settings_formio = {
    "display": "form",
    "components": [
        {
            "title": "Stage 2 configuratie",
            "theme": "primary",
            "collapsible": false,
            "key": "stage2Configuratie",
            "type": "panel",
            "label": "Panel",
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
                        "eq": "start-timeslot"
                    },
                    "type": "checkbox",
                    "input": true
                },
                {
                    "label": "Tijd vooraleer stage 2 zichtbaar wordt (seconden)",
                    "mask": false,
                    "spellcheck": false,
                    "tableView": false,
                    "defaultValue": 0,
                    "delimiter": false,
                    "requireDecimal": false,
                    "inputFormat": "plain",
                    "key": "stage-2-delay",
                    "type": "number",
                    "input": true
                }
            ]
        },
        {
            "title": "Stage 3 configuratie",
            "theme": "primary",
            "collapsible": false,
            "key": "stage3Configuratie1",
            "type": "panel",
            "label": "Stage 2 configuratie",
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
                        "eq": "start-timeslot"
                    },
                    "type": "checkbox",
                    "input": true
                },
                {
                    "label": "Tijd vooraleer stage 3 zichtbaar wordt (seconden)",
                    "mask": false,
                    "spellcheck": false,
                    "tableView": false,
                    "defaultValue": 0,
                    "delimiter": false,
                    "requireDecimal": false,
                    "inputFormat": "plain",
                    "key": "stage-3-delay",
                    "type": "number",
                    "input": true
                }
            ]
        }
    ]
}
