$(document).ready(function () {
    Formio.createForm(document.getElementById('register-form'), registration_form).then((form) => {
        // $.each(default_settings, function (k, v) {
        //     form.getComponent(k).setValue(v);
        // });
        // form.on('change', function (changed) {
        //     socketio_transmit_setting(changed.changed.component.key, changed.changed.value)
        // });
    });
});


