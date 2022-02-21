import re
def prepare_component(form, key, item):
    def iterate_over_components(container):
        for component in container['components']:
            if component['type'] == 'container':
                iterate_over_components(component)
            for key in ['html', 'content']:
                if key in component:
                    all_tags = re.findall('TAG\([^(]*\)', component[key])
                    flat = item.flat()
                    for tag in all_tags:
                        field = tag.split('(')[1].split(')')[0]
                        if field in flat:
                            component[key] = component[key].replace(tag, flat[field])

    container = search_component(form, key)
    iterate_over_components(container)
    container['hidden'] = False
    return form

def search_component(form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            return component
        if 'components' in component:
            found_component = search_component(component, key)
            if found_component: return found_component
    return None