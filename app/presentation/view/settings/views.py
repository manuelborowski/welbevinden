from flask import render_template
from flask_login import login_required

from app import admin_required
from app.application import socketio as msocketio, event as mevent
from . import settings
from app.application import settings as msettings
import json

@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    default_settings = msettings.get_configuration_settings()
    data = {
        'default': default_settings,
        'template': settings_formio,
    }
    return render_template('/settings/settings.html', data=data)


def update_settings_cb(msg, client_sid=None):
  try:
    data = msg['data']
    settings = json.loads(data['value'])
    msettings.set_setting_topic(settings)
    msettings.set_configuration_setting(data['setting'], data['value'])
    msocketio.send_to_room({'type': 'settings', 'data': {'status': True}}, client_sid)
  except Exception as e:
    msocketio.send_to_room({'type': 'settings', 'data': {'status': False, 'message': str(e)}}, client_sid)


def event_received_cb(msg, client_sid=None):
    mevent.process_event(msg['data']['event'])

msocketio.subscribe_on_type('settings', update_settings_cb)
msocketio.subscribe_on_type('event', event_received_cb)


from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
  {
    "display": "form",
    "components": [
      {
        "label": "General",
        "tableView": false,
        "key": "container",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Algemeen",
            "theme": "primary",
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
              }
            ]
          }
        ]
      },
      {
        "label": "Users",
        "tableView": false,
        "key": "container1",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Gebruikers",
            "theme": "primary",
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
        "label": "Student Care",
        "tableView": false,
        "key": "visitors",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Studenten ZORG",
            "theme": "primary",
            "collapsible": true,
            "key": "RegistratieTemplate1",
            "type": "panel",
            "label": "BEZOEKERS : Registratie template en e-mail",
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
                "key": "care-formio-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Lijst template (JSON)",
                "autoExpand": false,
                "tableView": true,
                "key": "care-datatables-template",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Student Intake",
        "tableView": false,
        "key": "visitors1",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Studenten INSCHRIJVEN",
            "theme": "primary",
            "collapsible": true,
            "key": "RegistratieTemplate1",
            "type": "panel",
            "label": "BEZOEKERS : Registratie template en e-mail",
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
                "key": "intake-formio-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Lijst template (JSON)",
                "autoExpand": false,
                "tableView": true,
                "key": "intake-datatables-template",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      }
    ]
  }