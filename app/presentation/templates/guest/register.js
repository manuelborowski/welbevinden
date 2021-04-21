var formio_form
$(document).ready(function () {
    Formio.createForm(document.getElementById('register-form'), registration_form).then((form) => {
        $.each(default_values, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error ) {
                return;
            }
        });
        formio_form = form
        form.on('change', form_changed);
        form.on('submit', function(submitted) {
            window.location.href = Flask.url_for(registration_endpoint, {form_data: JSON.stringify(submitted.data)});
        });
    });
});


function form_changed(changed) {
    formio_form.off('change', form_changed);
    var key = changed.changed.component.key;
    if (key.includes('select-boxes-')) {
        var val = changed.changed.value;
        var select_components = formio_form.getComponent('select-period-boxes').components;
        select_components.forEach(function (item, index) {
            item.setValue(0);
        });
        formio_form.getComponent(key).setValue(val);
    }
    setTimeout(function (){formio_form.on('change', form_changed)}, 1000);
}


