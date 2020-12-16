from app.presentation.layout.utils import flash_plus, format_datatable
from app.application.multiple_items import prepare_data_for_ajax
from app.application import tables
from flask import render_template


def ajax(table_configuration):
    try:
        data_list, total_count, filtered_count = prepare_data_for_ajax(table_configuration)
        datatable = format_datatable(data_list, total_count, filtered_count)
    except Exception as e:
        flash_plus(f'Tabel kan niet getoond worden (ajax)', e)
        datatable =  format_datatable([], 0, 0)
    return datatable


def show(table_configuration):
    filters = []
    config = None
    try:
        config = tables.prepare_config_table_for_view(table_configuration)
    except Exception as e:
        flash_plus(f'Tabel kan niet getoond worden (show)', e)
    return render_template('base_multiple_items.html', table_config=config, filters=filters)
