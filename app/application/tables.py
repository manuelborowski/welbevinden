from app.data.models import User
from app.data.utils import raise_error
from app import data

configuration = {
    'user': {
        'title': 'Gebruikers',
        'buttons': ['delete', 'add', 'edit'],
        'delete_message': u'Wilt u deze gebruiker(s) verwijderen?',
        'template': [
            {'name': 'row_action', 'data': 'row_action', 'width': '2%'},
            {'name': 'Gebruikersnaam', 'data': 'username', 'order_by': User.username, 'orderable': True},
            {'name': 'Voornaam', 'data': 'first_name', 'order_by': User.first_name, 'orderable': True},
            {'name': 'Naam', 'data': 'last_name', 'order_by': User.last_name, 'orderable': True},
            {'name': 'Email', 'data': 'email', 'order_by': User.email, 'orderable': True},
            {'name': 'Type', 'data': 'user_type', 'order_by': User.user_type, 'orderable': True},
            {'name': 'Login', 'data': 'last_login', 'order_by': User.last_login, 'orderable': True},
            {'name': 'Niveau', 'data': 'level', 'order_by': User.level, 'orderable': True}, ],
        'filter': [],
        # 'table_action': 'user.table_action',
        # 'table_ajax': 'user.table_ajax',
        # 'item_action': 'user.item_action',
        'item': {
            'edit': {'title': 'Wijzig een gebruiker', 'role': 'edit'},
            'add': {'title': 'Voeg een gebruiker toe', 'role': 'add'},
        },
        'href': [],
        'pre_filter': data.user.pre_filter,
        'format_data': data.user.format_data,
        'search_data': data.user.search_data,
        'default_order': (1, 'asc')
    },
}

def get_table_config(table):
    try:
        table_config = configuration[table]
        table_config['table_action'] = f'{table}.table_action'
        table_config['table_ajax'] = f'{table}.table_ajax'
        return table_config
    except Exception as e:
        raise_error('Kan de configuratietabel niet ophalen', e)

# create an exact copy of a configuration table
def deepcopy(table):
    if type(table) == dict:
        out = {}
        for k, v in table.items():
            if type(v) == list or type(v) == dict:
                out[k] = deepcopy(v)
            else:
                out[k] = v
    elif type(table) == list:
        out = []
        for i in table:
            if type(i) == list or type(i) == dict:
                out.append(deepcopy(i))
            else:
                out.append(i)
    else:
        out = table
    return out


# prepare the configuration table to be used in the html front end, i.e. remove unwanted members (function calls, ...)
def prepare_config_table_for_view(table):
    try:
        out = deepcopy(table)
        for i in out['template']:
            if 'order_by' in i:
                del i['order_by']
            if not 'orderable' in i:
                i['orderable'] = False
        if 'format_data' in out:
            del out['format_data']
        if 'pre_filter' in out:
            del out['pre_filter']
        if 'filter_data' in out:
            del out['filter_data']
        if 'post_processing' in out:
            del out['post_processing']
        if 'search_data' in out:
            del out['search_data']
        if 'get_filters' in out:
            del out['get_filters']
        if 'get_show_info' in out:
            del out['get_show_info']
        out['table_action'] = f'{out["view"]}.table_action'
        out['table_ajax'] = f'{out["view"]}.table_ajax'
    except Exception as e:
        raise_error('Kan de configuratietabel niet ophalen', e)
    return out


def prepare_item_config_for_view(table, action):
    try:
        item_config = table['item'][action]
        item_config['item_action'] = f'{table["view"]}.item_action'
        item_config['action'] = action
    except Exception as e:
        raise_error('Kan de itemconfiguratietabel niet ophalen', e)
    return item_config


