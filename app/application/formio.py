import re, datetime, sys
from app import log
# noinspection PyUnresolvedReferences
from bleach.sanitizer import Cleaner
from app.application.util import deepcopy

# iterate over the container, if a component contains a html or content property, replace the TAG(...) with
# the data provided by 'tag'
def fill_in_tags(component, flat):
    if component['type'] == 'container':
        for sub_component in component['components']:
            fill_in_tags(sub_component, flat)
    for key in ['html', 'content']:
        if key in component:
            all_tags = re.findall('TAG\([^(]*\)', component[key])
            for tag in all_tags:
                field = tag.split('(')[1].split(')')[0]
                link = None
                if '|' in field:
                    link, field = field.split('|')
                if field in flat:
                    if link:
                        component[key] = component[key].replace(tag, f"<a href='{str(flat[field])}'>{link}</a>")
                    else:
                        component[key] = component[key].replace(tag, str(flat[field]))


# find the given sub-component and update its tags.  Return the form because it is used to render the webpage
def prepare_sub_component(form, key, item ={}, additional_fields = {}):
    extract_sub_component(form, key, item, additional_fields)
    return form


# find the given sub-component and update its tags.  Return the component because it is used to send an email
def extract_sub_component(form, key, item ={}, additional_fields = {}):
    component = search_component(form, key)
    flat = item.flat() if item else {}
    flat.update(additional_fields)
    fill_in_tags(component, flat)
    component['hidden'] = False
    return component


def prepare_for_edit(form, flat={}, unfold=False):
    def cb(component, opaque):
        if component['key'] == 'photo':
            component['attrs'][0]['value'] = component['attrs'][0]['value'] + str(flat['photo'])

    iterate_components_cb(form, cb)
    return form


# update the register-form:
# -hide the 'header'
# -unhide additional components
# -make all components 'not required'
def prepare_for_add(form):
    def cb(component, opaque):
        if component['key'] == 'header':
            component['hidden'] = True
        if component['key'] == 'mail-confirm':
            component['hidden'] = True
            component['disabled'] = True
        if 'validate' in component and 'required' in component['validate']:
            component['validate']['required'] = False
        if 'tags' in component and 'show-when-edit' in component['tags']:
            component['hidden'] = False

    iterate_components_cb(form, cb)
    return form


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


# search, in a given hierarchical tree of components, for a component with the given 'key'
def search_component(form, key):
    components = None
    if 'components' in form:
        components = form['components']
    elif 'columns' in form:
        components = form['columns']
    if components:
        for component in components:
            if 'key' in component and component['key'] == key:
                return component
            if 'components' in component or 'columns' in component:
                found_component = search_component(component, key)
                if found_component: return found_component
    return None


# template is a formio component (with subcomponents, if needed)
# data is a list of structures.  Each entry creates a new component (from template) and the relevant properties are filled in (found via key)
def create_components(template, data):
    try:
        out = []
        for item in data:
            new_component = deepcopy(template)
            new_component["key"] = item["key"]
            for value in item['values']:
                component = search_component(new_component, value['key'])
                if component:
                    component[value['property']] = value['value']
            out.append(new_component)
        return out
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


#in a form, iterate over all components and execute callback for each component
def iterate_components_cb(form, cb, opaque=None):
    component_iter = iterate_components(form)
    try:
        while True:
            component = next(component_iter)
            if "key" in component:
                print(component["key"])
            cb(component, opaque)
    except StopIteration as e:
        pass

# iterate over all components.
# If a component is a container (i.e. contains a list of components, such as type container or columns), iterate first over de child-components
def iterate_components(form):
    components = []
    if 'components' in form:
        components = form['components']
    elif 'columns' in form:
        components = form['columns']
    for component in components:
        if 'components' in component or 'columns' in component or 'rows' in component:
            yield component
            yield from iterate_components(component)
        else:
            yield component
    if 'rows' in form:
        for row in form['rows']:
            for column in row:
                if 'components' in column or 'columns' in column or 'rows' in column:
                    yield column
                    yield from iterate_components(column)
                else:
                    yield column


def datetimestring_to_datetime(date_in, seconds=False):
    try:
        format_string = '%d/%m/%Y %H:%M:%S' if seconds else '%d/%m/%Y %H:%M'
        date_out = datetime.datetime.strptime(date_in, format_string)
        return date_out
    except:
        return None


def datestring_to_date(date_in):
    try:
        date_out = datetime.datetime.strptime(date_in, '%d/%m/%Y')
        return date_out.date()
    except:
        return None


# formio returns:
# 2022-3-4T13:34:23+02:00 OR SOMETIMES
# 2022-3-4T13:34:23.000Z OR SOMETIMES
# 2022-3-4 OR SOMETIMES
# 4/3/2022.  WHO KNOWS WHY???
def formiodate_to_datetime(formio_date):
    split_code = '.' if '.' in formio_date else '+'
    date_time = datetime.datetime.strptime(formio_date.split(split_code)[0], '%Y-%m-%dT%H:%M:%S')
    return date_time


# formio returns:
# 2022-3-4T13:34:23+02:00 OR SOMETIMES
# 2022-3-4T13:34:23.000Z OR SOMETIMES
# 2022-3-4 OR SOMETIMES
# 4/3/2022.  WHO KNOWS WHY???
def formiodate_to_date(formio_date):
    try:
        date = datetime.datetime.strptime(formio_date.split('T')[0], "%Y-%m-%d")
    except:
        date = datetime.datetime.strptime(formio_date, "%d/%m/%Y")
    return date.date()


def date_to_datestring(date):
    string = datetime.datetime.strftime(date, '%d/%m/%Y')
    return string


def datetime_to_datetimestring(date):
    string = datetime.datetime.strftime(date, '%d/%m/%Y %H:%M')
    return string


def datetime_to_formio_datetime(date):
    string = f"{datetime.datetime.strftime(date, '%Y-%m-%dT%H:%M')}:00+01:00"
    return string


def strip_html(input):
    cleaner = Cleaner(tags=[], attributes={}, styles=[], protocols=[], strip=True, strip_comments=True, filters=None)
    return cleaner.clean(input)