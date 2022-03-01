from app.presentation.layout.utils import flash_plus
from app.application.multiple_items import prepare_data_for_ajax
from app.application import tables
from flask import render_template, request, get_flashed_messages, jsonify


def ajax(table_configuration):
    try:
        data_list, total_count, filtered_count = prepare_data_for_ajax(table_configuration)
        datatable = format_datatable(table_configuration, data_list, total_count, filtered_count)
    except Exception as e:
        flash_plus(f'Tabel kan niet getoond worden (ajax)', e)
        datatable = format_datatable(table_configuration, [], 0, 0)
    return datatable


def update(table_configuration, fields):
    for field in fields:
        extra_field = {'name': field, 'data': field, 'width': '15%'}
        if extra_field in table_configuration['template']: continue
        table_configuration['template'].append(extra_field)


def show(table_configuration):
    filters = []
    show_info = []
    config = None
    if 'get_filters' in table_configuration:
        filters = table_configuration['get_filters']()
    try:
        config = tables.prepare_config_table_for_view(table_configuration)
    except Exception as e:
        flash_plus(f'Tabel kan niet getoond worden (show)', e)
    return render_template('base_multiple_items.html', table_config=config, filters=filters, show_info=show_info)


def format_datatable(table_configuration, data_list, total_count, filtered_count):
    #prepare for json/ajax
    output = {'draw': str(int(request.values['draw'])), 'recordsTotal': str(total_count),
              'recordsFiltered': str(filtered_count), 'data': data_list}
    # add the (non-standard) flash-tag to display flash-messages via ajax
    fml = get_flashed_messages()
    if not not fml:
        output['flash'] = fml
    if 'get_show_info' in table_configuration:
        output['show_info'] = table_configuration['get_show_info']()
    return  jsonify(output)