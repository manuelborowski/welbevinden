//Convert python True/False to js true/false
var False = false;
var True = true;

//If not exactly one checkbox is selected, display warning and return false, else return true
function is_exactly_one_checkbox_selected() {
    var nbr_checked = 0;
    $(".chbx_all").each(function (i) {
        if (this.checked) {
            nbr_checked++;
        }
    });
    if (nbr_checked == 1) {
        return true;
    } else {
        bootbox.alert("U moet exact één item selecteren");
        return false;
    }
}

//If one or more checkboxes are checked, return true.  Else display warning and return false
function is_at_least_one_checkbox_selected() {
    var nbr_checked = 0;
    $(".chbx_all").each(function (i) {
        if (this.checked) {
            nbr_checked++;
        }
    });
    if (nbr_checked == 0) {
        bootbox.alert("U hebt niets geselecteerd, probeer nogmaals");
        return false;
    } else {
        return true;
    }
}


//Before removing multiple entries, a confirm-box is shown.
function delete_item() {
    if (is_at_least_one_checkbox_selected()) {
        message = table_config.delete_message;
        bootbox.confirm(message, function (result) {
            if (result) {
                $("#button-pressed").val("delete");
                $("#action_form").submit();
            }
        });
    }
}

function add_item() {
    $("#button-pressed").val("add");
    $("#action_form").submit();
}

function view_item() {
    if (is_exactly_one_checkbox_selected()) {
        $("#button-pressed").val("view");
        $("#action_form").submit();
    }
}

function edit_item() {
    if (is_exactly_one_checkbox_selected()) {
        $("#button-pressed").val("edit");
        $("#action_form").submit();
    }
}

$(document).ready(function () {
    var filter_settings = {}

    //if a filter is changed, then the filter is applied by simulating a click on the filter button
    $(".table-filter").change(function () {
        $("#filter").click();
    });
    //The filter button of the filter is clicked
    $('#filter').click(function () {
        store_filter_settings();
        table.ajax.reload();
    });

    //The clear button of the filter is clicked
    $('#clear').click(function () {
        for (i = 0; i < filters.length; i++) {
            $("#" + filters[i].name).val(filters[i].default);
        }
        //emulate click on filter button
        $('#filter').trigger('click');
    });

    //Store locally in the client-browser
    function store_filter_settings() {
        for (i = 0; i < filters.length; i++) {
            filter_settings[filters[i].name] = $("#" + filters[i].name).val();
        }
        localStorage.setItem("Filter", JSON.stringify(filter_settings));
    }

    store_filter_settings(); //filters are applied when the page is loaded for the first time

    //Bugfix to repeat the table header at the bottom
    $("#datatable").append(
        $('<tfoot/>').append($("#datatable thead tr").clone())
    );

    //ellipsis
    $.each(config_columns, function (i, v) {
        if ("render" in v) {
            var cuttoff = v.render.cuttoff;
            var wordbreak = v.render.wordbreak;
            v.render = $.fn.dataTable.render.ellipsis(cuttoff, wordbreak, true);
        }
    });


    var datatable_config = {
        serverSide: true,
        stateSave: true,
        ajax: {
            url: Flask.url_for(table_config.table_ajax),
            type: 'POST',
            data: function (d) {
                return $.extend({}, d, filter_settings);
            }
        },
        pagingType: "full_numbers",
        columns: config_columns,
        language: {
            url: "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Dutch.json"
        },
        initComplete: function (settings, json) { //intercept flash messages when the table is loaded
            if ('flash' in json) {
                bootbox.alert(json['flash'].toString());
            }
        },
        createdRow: function (row, data, dataIndex, cells) {
            if (data.overwrite_row_color != "") {
                $(row).attr("style", "background-color: " + data.overwrite_row_color + ";");
            }
        },
        rowCallback: function (row, data, displayNum, displayIndex, dataIndex) {
            if (data.row_action != "") {
                row.cells[0].innerHTML = "<input type='checkbox' class='chbx_all' name='chbx' value='" + data.row_action + "'>" +
                    "<div value='" + data.row_action + "' class='pencil glyphicon glyphicon-pencil'></div>";

            }
        },
        preDrawCallback: function (settings) {
            busy_indication_on();
        },
        drawCallback: function (settings) {
            busy_indication_off();
            if (cell_to_color) {
                table.cells().every(function () {
                    if (this.data() in cell_to_color) {
                        $(this.node()).css("background-color", cell_to_color[this.data()]);
                        if (suppress_cell_content) {
                            $(this.node()).html("");
                        }
                    }
                });
            }
            if (table_config.buttons.includes("edit")) {
                //pencil is clicked
                $(".pencil").click(function () {
                    activity_id = $(this).attr("value");
                    checkbox = $("input[name$='chbx'][value=" + activity_id + "]");
                    checkbox.prop('checked', true);
                    edit_item();
                });
            }
            cell_toggle.display()
        },
    }

    if (table_config.suppress_dom) {
        datatable_config["filter"] = false;
        datatable_config["paging"] = false;
    } else {
        datatable_config["dom"] = "fiptlp";
    }

    if (current_user_is_at_least_admin) {
        datatable_config["lengthMenu"] = [50, 100, 200, 500, 1000];
    } else {
        datatable_config["lengthMenu"] = [50, 100, 200];
    }

    if ("default_order" in table_config) {
        datatable_config["order"] = [[table_config.default_order[0], table_config.default_order[1]]];
    }

    var table = $('#datatable').DataTable(datatable_config);

    function cell_edit_cb(type, data) {
        if ("status" in data) {
            if (data.status) {
                table.ajax.reload();
            }
        } else if ("reload-table" in data) {
            table.ajax.reload();
        }
    }

    if ('socketio_endpoint' in table_config) {
        socketio.subscribe_on_receive(table_config.socketio_endpoint, cell_edit_cb);
        socketio.start(null, null);
    }


    function update_cell_changed(data) {
        if ('socketio_endpoint' in table_config) {
            socketio.send_to_server(table_config.socketio_endpoint, data);
        } else {
            $.getJSON(Flask.url_for("{{table_config.cell_endpoint}}", {'jds': JSON.stringify(data)}),
                function (data) {
                    if (data.status) {
                        table.ajax.reload();
                    } else {
                        bootbox.alert('Fout: kan waarde niet aanpassen');
                    }
                }
            );
        }
    }

    function cell_edit_changed_cb(cell, row, old_value) {
        data = {
            'id': row.data().DT_RowId,
            'column': cell.index().column,
            'value': cell.data()
        }
        update_cell_changed(data);
    }

    function cell_toggle_changed_cb(cell, row, value) {
        data = {
            'id': row.data().DT_RowId,
            'column': cell.index().column,
            'value': value
        }
        update_cell_changed(data);
    }

    //test to cancel reload when column 1 is being edit
    // table.on('user-select', function ( e, dt, type, cell, originalEvent ) {
    //             if ( $(originalEvent.target).index() === 1 ) {
    //                 e.preventDefault();
    //             }
    //         });

    celledit_inputtypes = [];
    celledit_columns = []
    for (i = 0; i < config_columns.length; i++) {
        if ("celledit_options" in config_columns[i]) {
            entry = {};
            entry["column"] = i;
            celledit_columns.push(i);
            entry["type"] = "list";
            entry["options"] = [];
            for (j = 0; j < config_columns[i]["celledit_options"].length; j++) {
                opt = {
                    "value": config_columns[i]["celledit_options"][j][0],
                    "display": config_columns[i]["celledit_options"][j][1]
                };
                entry["options"].push(opt);
            }
            celledit_inputtypes.push(entry);
        } else if ("celledit" in config_columns[i]) {
            entry = {};
            entry["column"] = i;
            celledit_columns.push(i);
            entry["type"] = config_columns[i]["celledit"]
            entry["options"] = [];
            celledit_inputtypes.push(entry);
        }
    }

    if (celledit_inputtypes.length > 0) {
        // table.MakeCellsEditable("destroy");
        table.MakeCellsEditable({
            onUpdate: cell_edit_changed_cb,
            confirmationButton: {listenToKeys: true},
            columns: celledit_columns,
            inputTypes: celledit_inputtypes,
        });
    }

    celltoggle_columns = []
    $.each(config_columns, function (i, v) {
        celltoggle_columns.push(("celltoggle" in v) ? v["celltoggle"] : "");
    });

    function create_cell_toggle() {
        if (celltoggle_columns.length > 0) {
            // table.MakeCellsToggleable("destroy");
            table.MakeCellsToggleable({
                onUpdate: cell_toggle_changed_cb,
                columns: celltoggle_columns
            });
        }
    }

    var cell_toggle = new MakeCellsToggleable(table, {
        onUpdate: cell_toggle_changed_cb,
        columns: celltoggle_columns
    })

    if ("row_detail" in table_config) {
        //For an extra-measure, show the associated remarks as a sub-table
        var d_table_start = '<table cellpadding="5" cellspacing="0" border="2" style="padding-left:50px;">'
        var d_table_stop = '</table>'
        var d_header = '<tr><td>Datum</td><td>Leerling</td><td>LKR</td><td>KL</td><td>Les</td><td>Opmerking</td><td>Maatregel</td></tr>'

        function format_row_detail(data) {
            s = d_table_start;
            s += d_header;
            if (data) {
                for (i = 0; i < data.length; i++) {
                    s += '<tr>'
                    s = s + '<td>' + data[i].date + '</td>';
                    s = s + '<td>' + data[i].student.full_name + '</td>';
                    s = s + '<td>' + data[i].teacher.code + '</td>';
                    s = s + '<td>' + data[i].grade.code + '</td>';
                    s = s + '<td>' + data[i].lesson.code + '</td>';
                    s = s + '<td>' + data[i].subjects + '</td>';
                    s = s + '<td>' + data[i].measures + '</td>';
                    s += '</tr>'
                }
                s += d_table_stop;
                return s;
            }
            return 'Geen gegevens';
        }

        // Array to track the ids of the details displayed rows
        var detail_rows_cache = [];

        $('#datatable tbody').on('click', 'tr td.details-control', function () {
            var tr = $(this).closest('tr');
            var row = table.row(tr);
            var idx = $.inArray(tr.attr('DT_RowId'), detail_rows_cache);

            if (row.child.isShown()) {
                tr.removeClass('details');
                row.child.hide();
                detail_rows_cache.splice(idx, 1);
            } else {
                var tx_data = {"id": row.data().DT_RowId};
                $.getJSON(Flask.url_for('reviewed.get_row_detail', {'data': JSON.stringify(tx_data)}),
                    function (rx_data) {
                        if (rx_data.status) {
                            row.child(format_row_detail(rx_data.details)).show();
                            tr.addClass('details');
                            if (idx === -1) {
                                detail_rows_cache.push(tr.attr('DT_RowId'));
                            }
                        } else {
                            bootbox.alert('Fout: kan details niet ophalen');
                        }
                    });
            }
        });
    }

    if ("row_detail" in table_config) {
        //This function is called, each time the table is drawn
        table.on('draw', function () {
            //Row details
            $.each(detail_rows_cache, function (i, id) {
                $('#' + id + ' td.details-control').trigger('click');
            });
        });
    }

    //checkbox in header is clicked
    $("#select_all").change(function () {
        $(".chbx_all").prop('checked', this.checked);
    });

});

