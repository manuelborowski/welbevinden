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
    data = {'default': default_settings, 'template': settings_formio}
    return render_template('/settings/settings.html', data=data)


def update_settings_cb(msg, client_sid=None):
  try:
    data = msg['data']
    settings = json.loads(data['value'])
    msettings.set_setting_topic(settings)
    msocketio.broadcast_message({'type': 'settings', 'data': {'status': True}})
  except Exception as e:
    msocketio.broadcast_message({'type': 'settings', 'data': {'status': False, 'message': str(e)}})


msocketio.subscribe_on_type('settings', update_settings_cb)


from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
  {
    "display": "form",
    "components": [
      {
        "label": "Algemeen",
        "tableView": false,
        "key": "algemeen",
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
            "key": "gebruikers",
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
            "label": "templates-studenten",
            "tableView": false,
            "key": "templates-studenten",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Studenten",
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
                    "label": "Detail template (formio)",
                    "autoExpand": false,
                    "tableView": true,
                    "key": "student-formio-template",
                    "type": "textarea",
                    "input": true
                  },
                  {
                    "label": "Lijst template (JSON)",
                    "autoExpand": false,
                    "tableView": true,
                    "key": "student-datatables-template",
                    "type": "textarea",
                    "input": true
                  }
                ]
              }
            ]
          },
          {
            "label": "templates-cardpresso",
            "tableView": false,
            "key": "templates-cardpresso",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Cardpresso",
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
                    "label": "Detail template (formio)",
                    "autoExpand": false,
                    "tableView": true,
                    "key": "cardpresso-formio-template",
                    "type": "textarea",
                    "input": true
                  },
                  {
                    "label": "Lijst template (JSON)",
                    "autoExpand": false,
                    "tableView": true,
                    "key": "cardpresso-datatables-template",
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
        "theme": "warning",
        "collapsible": true,
        "key": "modules",
        "type": "panel",
        "label": "Panel",
        "input": false,
        "tableView": false,
        "components": [
          {
            "label": "General",
            "tableView": false,
            "key": "general",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Algmeen",
                "theme": "primary",
                "collapsible": true,
                "key": "general1",
                "type": "panel",
                "label": "General",
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
                    "label": "Externe databases NIET updaten",
                    "tableView": false,
                    "defaultValue": false,
                    "key": "general-inhibit-update-external-databases",
                    "type": "checkbox",
                    "input": true
                  },
                  {
                    "label": "Table",
                    "cellAlignment": "left",
                    "key": "table",
                    "type": "table",
                    "numRows": 4,
                    "numCols": 2,
                    "input": false,
                    "tableView": false,
                    "rows": [
                      [
                        {
                          "components": [
                            {
                              "label": "Haal de leerkrachten RFID uit Papercut",
                              "tableView": false,
                              "defaultValue": false,
                              "key": "chk-rfid-from-papercut",
                              "type": "checkbox",
                              "input": true,
                              "hideOnChildrenHidden": false
                            }
                          ]
                        },
                        {
                          "components": [
                            {
                              "label": "Haal de leerkrachten RFID uit Papercut",
                              "action": "event",
                              "showValidations": false,
                              "theme": "warning",
                              "tableView": false,
                              "key": "getTeacerRfidFromPapercut",
                              "conditional": {
                                "show": true,
                                "when": "general.chk-rfid-from-papercut",
                                "eq": "true"
                              },
                              "type": "button",
                              "event": "event-get-teacher-rfid-from-papercut",
                              "input": true,
                              "hideOnChildrenHidden": false
                            }
                          ]
                        }
                      ],
                      [
                        {
                          "components": [
                            {
                              "label": "Populate own database (from Smartschool and Papercut). Do this once!",
                              "tableView": false,
                              "defaultValue": false,
                              "key": "chk-populate-database",
                              "type": "checkbox",
                              "input": true,
                              "hideOnChildrenHidden": false
                            }
                          ]
                        },
                        {
                          "components": [
                            {
                              "label": "Populate Database",
                              "action": "event",
                              "showValidations": false,
                              "theme": "warning",
                              "tableView": false,
                              "key": "loadDatabase",
                              "conditional": {
                                "show": true,
                                "when": "general.chk-populate-database",
                                "eq": "true"
                              },
                              "type": "button",
                              "event": "event-populate-database",
                              "input": true,
                              "hideOnChildrenHidden": false
                            }
                          ]
                        }
                      ],
                      [
                        {
                          "components": [
                            {
                              "label": "Run update cycle now",
                              "tableView": false,
                              "defaultValue": false,
                              "key": "chk-update-database-now",
                              "type": "checkbox",
                              "input": true
                            }
                          ]
                        },
                        {
                          "components": [
                            {
                              "label": "Run update cycle now",
                              "action": "event",
                              "showValidations": false,
                              "theme": "warning",
                              "tableView": false,
                              "key": "updateDatabaseNow",
                              "conditional": {
                                "show": true,
                                "when": "general.chk-update-database-now",
                                "eq": "true"
                              },
                              "type": "button",
                              "event": "event-update-database-now",
                              "input": true
                            }
                          ]
                        }
                      ],
                      [
                        {
                          "components": [
                            {
                              "label": "Clear own database",
                              "tableView": false,
                              "key": "chk-clear-own-database",
                              "type": "checkbox",
                              "input": true,
                              "defaultValue": false
                            }
                          ]
                        },
                        {
                          "components": [
                            {
                              "label": "Clear own database",
                              "action": "event",
                              "showValidations": false,
                              "theme": "danger",
                              "tableView": false,
                              "key": "clearOwnDatabase",
                              "conditional": {
                                "show": true,
                                "when": "general.chk-clear-own-database",
                                "eq": "true"
                              },
                              "type": "button",
                              "event": "event-clear-own-database",
                              "input": true
                            }
                          ]
                        }
                      ]
                    ]
                  }
                ],
                "collapsed": true
              }
            ]
          },
          {
            "label": "Cron",
            "tableView": false,
            "key": "cron",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Cron",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate3",
                "type": "panel",
                "label": "Smartschool",
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
                    "label": "Cron template",
                    "labelPosition": "left-left",
                    "tooltip": "Check https://crontab.guru/ voor de layout van de cron template",
                    "tableView": true,
                    "persistent": false,
                    "key": "cron-scheduler-template",
                    "type": "textfield",
                    "labelWidth": 20,
                    "input": true
                  },
                  {
                    "label": "FROM Smartschool: update teachers (full name, ss username, ad username, ss internal number)",
                    "tableView": false,
                    "defaultValue": false,
                    "key": "smartschool-update-teachers",
                    "type": "checkbox",
                    "input": true
                  },
                  {
                    "label": "FROM Smartschool: update students (full name, ss username, ad username, ss internal number)",
                    "tableView": false,
                    "defaultValue": false,
                    "key": "smartschool-update-students",
                    "type": "checkbox",
                    "input": true
                  },
                  {
                    "label": "FROM Wisa: update teachers",
                    "tableView": false,
                    "defaultValue": false,
                    "key": "wisa-update-teachers",
                    "type": "checkbox",
                    "input": true
                  },
                  {
                    "label": "FROM Wisa: update students ",
                    "tableView": false,
                    "defaultValue": false,
                    "key": "wisa-update-students",
                    "type": "checkbox",
                    "input": true
                  },
                  {
                    "label": "FROM Cardpresso: update students (RFID code)",
                    "tableView": false,
                    "defaultValue": false,
                    "key": "cardpresso-update-students",
                    "type": "checkbox",
                    "input": true
                  },
                  {
                    "label": "TO AD: update accounts",
                    "tableView": false,
                    "defaultValue": false,
                    "key": "ad-update-accounts",
                    "type": "checkbox",
                    "input": true
                  },
                  {
                    "label": "TO Papercut: update accounts",
                    "tableView": false,
                    "defaultValue": false,
                    "key": "papercut-update-accounts",
                    "type": "checkbox",
                    "input": true
                  }
                ],
                "collapsed": true
              }
            ]
          },
          {
            "label": "Smartschool",
            "tableView": false,
            "key": "smartschool",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Smartschool",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate1",
                "type": "panel",
                "label": "Smartschool",
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
                    "label": "Teacher groupname",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "smartschool-teacher-group",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  },
                  {
                    "label": "WebAPI URL",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "smartschool-api-url",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  },
                  {
                    "label": "WebAPI Key",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "smartschool-api-key",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  }
                ],
                "collapsed": true
              }
            ]
          },
          {
            "label": "Cardpresso",
            "tableView": false,
            "key": "cardpresso",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Cardpresso",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate2",
                "type": "panel",
                "label": "Smartschool",
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
                    "label": "URL to server",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "cardpresso-url",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  },
                  {
                    "label": "Server login",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "cardpresso-login",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  },
                  {
                    "label": "Server password",
                    "labelPosition": "left-left",
                    "spellcheck": false,
                    "tableView": true,
                    "persistent": false,
                    "key": "cardpresso-password",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  },
                  {
                    "label": "Excel file location (use / or \\\\)",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "cardpresso-file",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  }
                ],
                "collapsed": true
              }
            ]
          },
          {
            "label": "Active Directory",
            "tableView": false,
            "key": "active-directory",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Active Directory",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate4",
                "type": "panel",
                "label": "Cardpresso",
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
                    "label": "URL to server",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "ad-url",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  },
                  {
                    "label": "Server login",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "ad-login",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  },
                  {
                    "label": "Server password",
                    "labelPosition": "left-left",
                    "spellcheck": false,
                    "tableView": true,
                    "persistent": false,
                    "key": "ad-password",
                    "type": "textfield",
                    "input": true,
                    "labelWidth": 20
                  }
                ],
                "collapsed": true
              }
            ]
          },
          {
            "label": "Papercut",
            "tableView": false,
            "key": "papercut",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Papercut",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate6",
                "type": "panel",
                "label": "Active Directory",
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
                    "label": "Server",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "papercut-server-url",
                    "type": "textfield",
                    "labelWidth": 20,
                    "input": true
                  },
                  {
                    "label": "Server port",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "papercut-server-port",
                    "type": "textfield",
                    "labelWidth": 20,
                    "input": true
                  },
                  {
                    "label": "Server authentication token",
                    "labelPosition": "left-left",
                    "spellcheck": false,
                    "tableView": true,
                    "persistent": false,
                    "key": "papercut-auth-token",
                    "type": "textfield",
                    "labelWidth": 20,
                    "input": true
                  }
                ],
                "collapsed": true
              }
            ]
          },
          {
            "label": "Wisa",
            "tableView": false,
            "key": "wisa",
            "type": "container",
            "input": true,
            "components": [
              {
                "title": "Wisa",
                "theme": "primary",
                "collapsible": true,
                "key": "RegistratieTemplate4",
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
                    "label": "Columns",
                    "columns": [
                      {
                        "components": [
                          {
                            "label": "Laad gegevens van Wisa",
                            "tableView": false,
                            "defaultValue": false,
                            "key": "check-load-from-wisa",
                            "type": "checkbox",
                            "input": true
                          }
                        ],
                        "width": 3,
                        "offset": 0,
                        "push": 0,
                        "pull": 0,
                        "size": "md",
                        "currentWidth": 3
                      },
                      {
                        "components": [
                          {
                            "label": "Laad gegevens uit Wisa",
                            "showValidations": false,
                            "theme": "danger",
                            "tableView": false,
                            "key": "button-load-from-wisa",
                            "conditional": {
                              "show": true,
                              "when": "wisa.check-load-from-wisa",
                              "eq": "true"
                            },
                            "type": "button",
                            "saveOnEnter": false,
                            "input": true
                          }
                        ],
                        "width": 6,
                        "offset": 0,
                        "push": 0,
                        "pull": 0,
                        "size": "md",
                        "currentWidth": 6
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
                            "label": "Laad foto's",
                            "tableView": false,
                            "defaultValue": false,
                            "key": "check-load-photos",
                            "type": "checkbox",
                            "input": true
                          }
                        ],
                        "width": 3,
                        "offset": 0,
                        "push": 0,
                        "pull": 0,
                        "size": "md",
                        "currentWidth": 3
                      },
                      {
                        "components": [
                          {
                            "label": "Laad foto's",
                            "showValidations": false,
                            "theme": "danger",
                            "tableView": false,
                            "key": "button-load-photos",
                            "conditional": {
                              "show": true,
                              "when": "wisa.check-load-photos",
                              "eq": "true"
                            },
                            "type": "button",
                            "input": true,
                            "saveOnEnter": false
                          }
                        ],
                        "width": 6,
                        "offset": 0,
                        "push": 0,
                        "pull": 0,
                        "size": "md",
                        "currentWidth": 6
                      }
                    ],
                    "key": "columns1",
                    "type": "columns",
                    "input": false,
                    "tableView": false
                  },
                  {
                    "label": "URL",
                    "labelPosition": "left-left",
                    "tableView": true,
                    "persistent": false,
                    "key": "wisa-url",
                    "type": "textfield",
                    "labelWidth": 20,
                    "input": true
                  },
                  {
                    "label": "Server login",
                    "labelPosition": "left-left",
                    "labelWidth": 20,
                    "tableView": true,
                    "persistent": false,
                    "key": "wisa-login",
                    "type": "textfield",
                    "input": true
                  },
                  {
                    "label": "Server password",
                    "labelPosition": "left-left",
                    "labelWidth": 20,
                    "spellcheck": false,
                    "tableView": true,
                    "persistent": false,
                    "key": "wisa-password",
                    "type": "textfield",
                    "input": true
                  },
                  {
                    "label": "Huidig schooljaar",
                    "labelPosition": "left-left",
                    "spellcheck": false,
                    "tableView": true,
                    "persistent": false,
                    "key": "wisa-schoolyear",
                    "type": "textfield",
                    "labelWidth": 20,
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