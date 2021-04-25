var _form = null;
$(document).ready(function () {
    socketio.start(null, null);
    socketio.subscribe_on_receive("settings", socketio_receive_settings);
    socketio.subscribe_on_receive("event", socketio_event_ack);
    Formio.createForm(document.getElementById('configuration-settings'), data.template).then((form) => {
        _form = form
        $.each(data.default, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error) {
                return;
            }
        });
        form.on('submit', function(submission) {
            socketio_transmit_setting('data', JSON.stringify((submission.data)))
        })
        form.on('event-get-teacher-rfid-from-papercut', function(submission) {
            busy_indication_on();
            socketio_transmit_event('event-get-teacher-rfid-from-papercut')
            _form.getComponent("chk-rfid-from-papercut").setValue(false);
        })
        form.on('event-populate-database', function(submission) {
            busy_indication_on();
            socketio_transmit_event('event-populate-database')
            _form.getComponent("chk-populate-database").setValue(false);
        })
        form.on('event-update-database-now', function(submission) {
            busy_indication_on();
            socketio_transmit_event('event-update-database-now')
            _form.getComponent("chk-update-database-now").setValue(false);
        })
        form.on('event-clear-own-database', function(submission) {
            busy_indication_on();
            socketio_transmit_event('event-clear-own-database')
            _form.getComponent("chk-clear-own-database").setValue(false);
        })
        $('.formio-component-panel [ref=header]').on('click', panel_header_clicked);
    });
});


function socketio_receive_settings(type, data) {
    _form.emit('submitDone')
    setTimeout(function() {$("#configuration-settings .alert").css("display", "none");}, 1000);
    if (!data.status) {
        bootbox.alert("Warning, following error appeared:<br>" + data.message);
    }
}

function socketio_event_ack(type, data) {
    busy_indication_off();
    if (data.status) {
        bootbox.alert(data.message);
    } else {
        bootbox.alert("Warning, following error appeared:<br>" + data.message);
    }
}

function socketio_transmit_setting(setting, value) {
    socketio.send_to_server('settings', {setting: setting, value: value});
    return false;
}

function socketio_transmit_event(event) {
    socketio.send_to_server('event', {event: event});
    return false;
}

function panel_header_clicked(event) {
    event.stopImmediatePropagation();
    $("[ref=datagrid-timeslot-list-row]").on("change", function(e) {
        var row_index = e.currentTarget.rowIndex;
        timeslot_component.rows[row_index - 1]['timeslot-action'].setValue('U');
    })
    $('.formio-component-panel  [ref=header]').on('click', panel_header_clicked);
}
