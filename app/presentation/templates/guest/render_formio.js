let formio_form
let template = 'template' in data ? data.template : null;
let defaults = 'defaults' in data ? data.defaults : null;
let submit = 'submit' in data ? data.submit : null;
$(document).ready(function () {
    const form_options = {
        sanitizeConfig: {addTags: ['iframe'], addAttr: ['allow'], ALLOWED_TAGS: ['iframe'], ALLOWED_ATTR: ['allow']},
        noAlerts: true,
    }
    Formio.createForm(document.getElementById('register-form'), template, form_options).then((form) => {
        $.each(defaults, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error) {
                console.log("skipped ", k, v);
            }
        });
        formio_form = form
        form.on('change', form_changed);
        if (submit) {
            form.on('submit', function (submitted) {
                if (submit.data) {
                    window.location.href = Flask.url_for(submit.endpoint, {form_data: encodeURIComponent(encodeURIComponent(JSON.stringify(submitted.data)))});
                } else {
                    window.location.href = Flask.url_for(submit.endpoint);
                }
            });
        }
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


