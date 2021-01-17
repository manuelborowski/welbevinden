from app.application import reservation as mreservation, settings as msettings
import json

false = False
true = True
null = None

def prepare_registration_form(registration_code):
    default_values, available_periods = mreservation.get_default_values(registration_code)
    new_register_formio = json.loads(msettings.get_register_template())
    update_available_periods(available_periods, new_register_formio, 'select-period-boxes')
    return {
        'default': default_values,
        'form': new_register_formio
    }


def update_available_periods(periods, form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            select_template = component['components'][0]
            data_template = component['components'][0]['data']['values'][0]
            component['components'] = []
            for period in periods:
                if period['boxes_available'] <= 0:
                    continue
                new = dict(select_template)
                new['data'] = dict({'values': []})
                for value in range(period['boxes_available'] + 1):
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


