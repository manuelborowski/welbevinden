$(document).ready(function () {
        socketio.subscribe_on_receive("settings", socketio_receive_settings);
        Formio.createForm(document.getElementById('configuration-settings'), settings_form).then((form) => {
        $.each(default_settings, function (k, v){
            try {
                form.getComponent(k).setValue(v);
            }
            catch (e) {
                console.log("Could not set default setting: ", k, v);
            }
        });
        form.on('button-send-invite-emails', function (changed) {
            socketio_transmit_event('button-send-invite-emails');
        });
        form.on('change', function (changed) {
            socketio_transmit_setting(changed.changed.component.key ,changed.changed.value);
        });
    });
});


function socketio_receive_settings(type, data) {
}


function socketio_transmit_event(event) {
    socketio.send_to_server('event', {event: event});
    return false;
}

function socketio_transmit_setting(setting, value) {
    socketio.send_to_server('settings', {setting: setting, value: value});
    return false;
}