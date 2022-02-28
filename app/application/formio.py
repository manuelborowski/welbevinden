import re, datetime

# iterate over the container, if a component contains a html or content property, replace the TAG(...) with
# the data provided by 'tag'
def fill_in_tags(container, flat):
    for component in container['components']:
        if component['type'] == 'container':
            fill_in_tags(component, flat)
        for key in ['html', 'content']:
            if key in component:
                all_tags = re.findall('TAG\([^(]*\)', component[key])
                for tag in all_tags:
                    field = tag.split('(')[1].split(')')[0]
                    if field in flat:
                        component[key] = component[key].replace(tag, flat[field])


# find the given sub-component and update its tags
def prepare_sub_component(form, key, item, additional_fields = {}):
    flat = item.flat() if item else {}
    flat.update(additional_fields)
    container = search_component(form, key)
    fill_in_tags(container, flat)
    container['hidden'] = False
    return form


# update the register-form:
# -hide the 'header'
# -unhide additional components
# -make all components 'not required'
def prepare_for_edit(form):
    def cb(component):
        if component['key'] == 'header':
            component['hidden'] = True
        if 'validate' in component and 'required' in component['validate']:
            component['validate']['required'] = False
        if 'tags' in component and 'show-when-edit' in component['tags']:
            component['hidden'] = False

    iterate_components_cb(form, cb)
    return form


# search, in a given hierarchical tree of components, for a component with the given 'key'
def search_component(form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            return component
        if 'components' in component:
            found_component = search_component(component, key)
            if found_component: return found_component
    return None


#in a form, iterate over all components and execute callback for each component
def iterate_components_cb(form, cb):
    c_iter = iterate_components(form)
    try:
        while True:
            c = next(c_iter)
            cb(c)
    except StopIteration as e:
        pass


def iterate_components(form):
    components = form['components'] if 'components' in form else form['columns']
    for component in components:
        if 'components' in component or 'columns' in component:
            yield from iterate_components(component)
        else:
            yield component


def formiodate_to_datetime(formio_date):
    date_time = datetime.datetime.strptime(':'.join(formio_date.split(':')[:2]), '%d/%m%Y-T%H:%M')
    return date_time


def formiodate_to_date(formio_date):
    date = datetime.datetime.strptime(formio_date, "%d/%m/%Y")
    return date


def datetime_to_formiodatetime(date):
    string = f"{datetime.datetime.strftime(date, '%d/%m/%YT%H:%M')}:00+01:00"
    return string


