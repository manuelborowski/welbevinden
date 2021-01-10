$(document).ready(function () {
        socketio.subscribe_on_receive("settings", socketio_receive_settings);
        Formio.createForm(document.getElementById('configuration-settings'), settings_form).then((form) => {
        $.each(default_settings, function (k, v){
            form.getComponent(k).setValue(v);
        });
        form.on('change', function (changed) {
            socketio_transmit_setting(changed.changed.component.key ,changed.changed.value)
        });
    });
});


function socketio_receive_settings(type, data) {
}


function socketio_transmit_setting(setting, value) {
    socketio.send_to_server('settings', {setting: setting, value: value});
    return false;
}