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
                "title": "Algemeen",
                "theme": "primary",
                "collapsible": true,
                "key": "algemeen",
                "type": "panel",
                "label": "Algemeen",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Uitnodigingse-mails worden verzonden",
                        "tableView": false,
                        "defaultValue": false,
                        "persistent": false,
                        "key": "enable-send-invite-email",
                        "type": "checkbox",
                        "input": true
                    },
                    {
                        "label": "Bevestigingse-mails worden verzonden",
                        "tableView": false,
                        "defaultValue": false,
                        "persistent": false,
                        "key": "enable-send-ack-email",
                        "type": "checkbox",
                        "input": true
                    }
                ],
                "collapsed": true
            },
            {
                "title": "BEZOEKERS : Registratie template en e-mail",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate1",
                "type": "panel",
                "label": "BEZOEKERS : Registratie template en e-mail",
                "input": false,
                "tableView": false,
                "components": [
                    {
                        "label": "Uitnodigings email: onderwerp",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "invite-mail-subject-template",
                        "type": "textarea",
                        "input": true
                    },
                    {
                        "label": "Uitnodigings email: inhoud",
                        "autoExpand": false,
                        "tableView": true,
                        "key": "invite-mail-content-template",
                        "type": "textarea",
                        "input": true
                    },
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
                        "label": "Aantal keer dat een e-mail geprobeerd wordt te verzenden",
                        "labelPosition": "left-left",
                        "mask": false,
                        "spellcheck": false,
                        "tableView": false,
                        "delimiter": false,
                        "requireDecimal": false,
                        "inputFormat": "plain",
                        "key": "email-send-max-retries",
                        "type": "number",
                        "input": true
                    },
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