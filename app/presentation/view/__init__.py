from app.application import reservation as mreservation, settings as msettings
import json

false = False
true = True
null = None


def prepare_registration_form(code):
    ret = mreservation.prepare_reservation(code)
    if ret.result == ret.Result.E_OK:
        available_timeslots = ret.ret['available_timeslots']
        template = ret.ret['template']
        update_available_timeslots(available_timeslots, template, 'radio-timeslot')
    return ret


def update_available_timeslots(timeslots, form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            values = []
            # component['components'] = []
            for timeslot in timeslots:
                if timeslot['available'] <= 0:
                    continue
                new = {
                    'label': timeslot['label'],
                    'value': timeslot['value'],
                    'shortcut': '',
                }
                values.append(new)
                if timeslot['default']:
                    component['defaultValue'] = timeslot['value']
            component['values'] = values
            return
        if 'components' in component:
            update_available_timeslots(timeslots, component, key)
    return


