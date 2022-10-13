var _form = null;
$(document).ready(function () {
    socketio.start(null, null);
    socketio.subscribe_on_receive("settings", socketio_settings_ack);
    socketio.subscribe_on_receive("event", socketio_event_ack);
    load_formio_form();

});


async function load_formio_form() {
    const options = {};
    await Formio.createForm(document.getElementById('configuration-settings'), data.template, options).then(form => {
        _form = form
        var button_id; // hack to set the value of the button, which was just clicked, to false again.
        $.each(data.default, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error) {
                return;
            }
        });
        form.on('submit', function (submission) {
            socketio_transmit_setting('data', JSON.stringify((submission.data)))
            _form.getComponentById(button_id).setValue(false);
        })
        form.on('submitButton', button => {
            button_id = button.instance.id;
        });

        form.on('copy-to-clipboard-ouders-link', container => {
            console.log(container["url-to-ouders-survey"]);
            navigator.clipboard.writeText(container["url-to-ouders-survey"]);
        });
        form.on('copy-to-clipboard-leerlingen-link', container => {
            console.log(container["url-to-leerlingen-survey"]);
            navigator.clipboard.writeText(container["url-to-leerlingen-survey"]);
        });
        form.on('event-load-leerlingen-lijst', container => {
            const school = container["hidden-school-naam"]
            const file_selector = document.getElementById(`${school}-input-file-select-leerlingen-lijst`);
            file_selector.value = null;
            // Attach an change-event-handler to the input-file-element so to start uploading and processing the file
            file_selector.addEventListener('change', async e => {
                const ret = await fetch(Flask.url_for("settings.upload", {subject: "leerlingenlijst", school}), {method: 'POST', body: file_selector.files[0]})
                const status = await ret.json();
                if (status.status) {
                    bootbox.alert(status.data);
                    const indicator_key = `${school}-upload-leerlingen-lijst-indicator`;
                    _form.getComponent(indicator_key).setValue('Er zijn studenten uploaded, ververs browserscherm');
                } else {
                    bootbox.alert('Foutmelding: ' + status.data);
                }
            }, {once:true})
            file_selector.click();
        })
        form.on('event-clear-leerlingen-lijst', async container => {
            const school = container["hidden-school-naam"]
            const ret = await fetch(Flask.url_for("settings.clear", {subject: "leerlingenlijst", school}), {method: 'POST'})
                const status = await ret.json();
                if (status.status) {
                    bootbox.alert(status.data);
                    const indicator_key = `${school}-upload-leerlingen-lijst-indicator`;
                    _form.getComponent(indicator_key).setValue('De lijst is gewist, ververs browserscherm');
                } else {
                    bootbox.alert('Foutmelding: ' + status.data);
                }
        })
    });
}


function socketio_settings_ack(type, data) {
    _form.emit('submitDone')
    // setTimeout(function() {$("#configuration-settings .alert").css("display", "none");}, 1000);
    setTimeout(function () {
        document.querySelectorAll("[ref=buttonMessageContainer]").forEach(b => b.style.display = "none");
        document.querySelectorAll("[ref=button]").forEach(b => {
            b.classList.remove('btn-success');
            b.classList.remove('submit-success');
        });
    }, 1000);
    if (!data.status) {
        bootbox.alert("Warning, following error appeared:<br>" + data.message);
    }
    busy_indication_off();
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
    busy_indication_on();
    socketio.send_to_server('settings', {setting: setting, value: value});
    return false;
}

function socketio_transmit_event(event) {
    socketio.send_to_server('event', {event: event});
    return false;
}
