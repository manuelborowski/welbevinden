let formio
let form_name = 'form' in data ? data.form : null;
let extra = 'extra' in data ? data.extra : {};
let get_form_endpoint = 'get_form_endpoint' in data ? data.get_form_endpoint : "";
let cancel_endpoint = 'cancel_endpoint' in data ? data.cancel_endpoint : "";

$(document).ready(function () {
    load_new_form(form_name, extra);
});


const load_new_form = async (form_name, extra = {}) => {
    const form_options = {
        sanitizeConfig: {addTags: ['iframe'], addAttr: ['allow'], ALLOWED_TAGS: ['iframe'], ALLOWED_ATTR: ['allow']},
        // noAlerts: true,
    }
    const ret = await fetch(Flask.url_for(get_form_endpoint, {form: form_name, extra}))
    const form_data = await ret.json();
    if (form_data.status) {
        formio = await Formio.createForm(document.getElementById('formio-form'), form_data.data.template, form_options)
        if ('defaults' in form_data.data) {
            Object.entries(form_data.data.defaults).forEach(([k, v]) => {
                try {
                    formio.getComponent(k).setValue(v);
                } catch (error) {
                    console.log("skipped ", k, v);
                }
            });
        }
        formio.on('change', form_changed);
        formio.on('submit', async submitted => {
            let extra = null;
            if ('post_data_endpoint' in form_data.data) {
                const ret = await fetch(Flask.url_for(form_data.data.post_data_endpoint), {
                    method: 'POST',
                    body: JSON.stringify(submitted.data),
                });
                const status = await ret.json();
                if (status.status) {
                    extra = status.data;
                } else {
                    alert(`Fout bij het opslaan:\n ${status.data}`)
                    document.location.reload();
                }
            }
            if ('form_on_submit' in form_data.data) {
                load_new_form(form_data.data.form_on_submit, extra);
            }
            if ('submit_endpoint' in form_data.data) {
                document.location.href = Flask.url_for(form_data.data['submit_endpoint'])
            }
        });
        formio.on('cancel', () => {
            if ('cancel_endpoint' in form_data.data) {
                document.location.href = Flask.url_for(form_data.data['cancel_endpoint'])
            }
        });
    } else {
        alert(`Fout bij het ophalen van een form:\n ${form_data.data}`)
        document.location.reload();
    }
}

function form_changed(changed) {
    formio.off('change', form_changed);
    var key = changed.changed.component.key;
    if (key.includes('select-boxes-')) {
        var val = changed.changed.value;
        var select_components = formio.getComponent('select-period-boxes').components;
        select_components.forEach(function (item, index) {
            item.setValue(0);
        });
        formio.getComponent(key).setValue(val);
    }
    setTimeout(function () {
        formio.on('change', form_changed)
    }, 1000);
}
