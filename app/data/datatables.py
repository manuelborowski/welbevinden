from sqlalchemy import desc
from app.data.settings import get_datatables_config

class DatatableConfig:
    def __init__(self, view, title):
        self.view = view
        self.title = title
        self.template = get_datatables_config(self.view)

    buttons = []
    href = []
    cell_to_color = None
    suppress_cell_content = None
    enable_column_visible_selector = True
    enable_persistent_filter_settings = True

    def show_filter_elements(self):
        return []

    def pre_sql_query(self):
        return None

    def pre_sql_filter(self, q, filter):
        return q

    def pre_sql_search(self, search):
        return None

    def pre_sql_order(self, q, on, direction):
        return q.order_by(desc(on)) if direction == 'desc' else q.order_by(on)

    def pre_sql_paginate(self, q, start, stop):
        return q.slice(start, stop)

    def format_data(self, l, count):
        return count, l

    def post_sql_filter(self, l, filter, count):
        return count, l

    def post_sql_search(self, l, search, count):
        return count, l

    def post_sql_order(self, l, on, direction):
        return l

    def post_sql_paginate(self, l, start, length):
        return l

    def show_info(self):
        return []

    def get_right_click(self):
        return {}

    def create_table_config(self):
        return {
            "buttons": self.buttons,
            "href": self.href,
            "enable_column_visible_selector": self.enable_column_visible_selector,
            "enable_persistent_filter_settings": self.enable_persistent_filter_settings,
            "template": self.template,
            "filters": self.show_filter_elements(),
            "table_action": f"{self.view}.table_action",
            "table_ajax": f"{self.view}.table_ajax",
            "show_info": self.show_info(),
            "right_click": self.get_right_click(),
            "cell_to_color": self.cell_to_color,
            "suppress_cell_content": self.suppress_cell_content
        }
