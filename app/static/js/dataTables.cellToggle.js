/*! CellToggle 0.0.1
 * ©2021 Manuel Borowski
 */

/**
 * @summary     CellToggle
 * @description Creates a toggle button in a cell
 * @version     0.0.1
 *
 * This source file is free software, available under the following license:
 *   MIT license - http://datatables.net/license/mit
 *
 * This source file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the license files for details.
 *
 * For details please refer to: http://www.datatables.net
 */

jQuery.fn.dataTable.Api.register('MakeCellsToggleable()', function (settings) {
    var table = this.table();
    var toggle_columns = []
    $.each(settings.columns, function (i, v) {
        if (v !== "") toggle_columns.push(i);
    });

    // Destroy
    if (settings === "destroy") {
        $(table.body()).off("click", "td");
        table = null;
    }

    if (table != null) {
        // On cell click
        $(table.body()).on('click', 'td', function () {
            var currentColumnIndex = table.cell(this).index().column;
            if (toggle_columns.includes(currentColumnIndex)) {

                var row = table.row($(this).parents('tr'));
                var cell = table.cell(this).node();
                var cell_content = table.cell(this).data();
                var checked_found = $($.parseHTML(cell_content)).find("input:checkbox:checked").val();
                var current_value = typeof(checked_found) !== "undefined"
                var template = get_toggle_template(!current_value);
                $(cell).html(template);
                settings.onUpdate(table.cell(this), row, !current_value);
            }
        });
    }

    $.each(toggle_columns, function (ci, cv) {
        $.each(table.column(cv).data(), function (ri, rv) {
            var template = get_toggle_template(rv);
            table.cell({row: ri, column: cv}).data(template)
        })
    });

    function get_toggle_template(value) {
        return "<div class='custom-control custom-switch'><input id='ejbeatycelledit' type='checkbox' class='custom-control-input' onfocusout='$(this).updateEditableCell(this)' " + (value ? "checked" : "") + "></input><label class='custom-control-label' for='customSwitch1'></label></div>";
    }

});

