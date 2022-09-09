from app.presentation.view import false, true, null

update_password = {
    "update-password":
        {
            "display": "form",
            "components": [
                {
                    "title": "Paswoord aanpassen",
                    "theme": "primary",
                    "collapsible": false,
                    "key": "nieuwPaswoordGeven",
                    "type": "panel",
                    "label": "Panel",
                    "input": false,
                    "tableView": false,
                    "components": [
                        {
                            "label": "Nieuw paswoord voor:",
                            "autoExpand": false,
                            "disabled": true,
                            "tableView": true,
                            "key": "new-password-user-name",
                            "type": "textarea",
                            "input": true
                        },
                        {
                            "label": "Nieuw paswoord (mag leeg zijn):",
                            "tooltip": "Geef een geldig paswoord (min. 8 karakters, grote letters, kleine letters, cijfers, leestekens).\nJe eigen naam mag er niet inzitten.\nMag leeg zijn (geen paswoord).",
                            "showCharCount": true,
                            "tableView": false,
                            "calculateServer": true,
                            "key": "new-password",
                            "type": "password",
                            "input": true,
                            "protected": true
                        },
                        {
                            "label": "Gebruiker moet paswoord aanpassen bij eerste keer aanmelden",
                            "tableView": false,
                            "key": "user-must-update-password",
                            "type": "checkbox",
                            "input": true,
                            "defaultValue": false
                        },
                        {
                            "label": "Columns",
                            "columns": [
                                {
                                    "components": [
                                        {
                                            "label": "Aanpassen",
                                            "showValidations": false,
                                            "theme": "success",
                                            "disableOnInvalid": true,
                                            "tableView": false,
                                            "key": "submit",
                                            "type": "button",
                                            "input": true,
                                            "saveOnEnter": false
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
                                            "label": "Annuleren",
                                            "action": "event",
                                            "showValidations": false,
                                            "theme": "warning",
                                            "tableView": false,
                                            "key": "annuleren",
                                            "type": "button",
                                            "input": true,
                                            "event": "cancel"
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
                        }
                    ]
                }
            ]
        }
}
