let formio
let form_name = 'form' in data ? data.form : null;
let extra = 'extra' in data ? data.extra : {};
let get_form_endpoint = 'get_form_endpoint' in data ? data.get_form_endpoint : "";
let cancel_endpoint = 'cancel_endpoint' in data ? data.cancel_endpoint : "";
let formio_local_storage = {}

$(document).ready(function () {
    load_new_form(form_name, extra);
});


const load_new_form = async (form_name, extra = {}) => {
    const form_options = {
        sanitizeConfig: {addTags: ['iframe'], addAttr: ['allow'], ALLOWED_TAGS: ['iframe'], ALLOWED_ATTR: ['allow']},
        // noAlerts: true,
    }
    //Get form from server
    const ret = await fetch(Flask.url_for(get_form_endpoint, {form: form_name, extra}))
    const form_data = await ret.json();
    if (form_data.status) {
        //Render and display form
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
        // check if form data is present in the local browser
        formio_local_storage = JSON.parse(localStorage.getItem(`Formio-${form_name}`)) || {};
        if (formio_local_storage) {
            Object.entries(formio_local_storage).forEach(([k, v]) => {
                try {
                    formio.getComponent(k).setValue(v);
                } catch (error) {
                    console.log("skipped ", k, v);
                }
            });
        }
        //store the data in the local browser on regular intervals
        setInterval(() =>{
            const data = formio.submission.data;
            localStorage.setItem(`Formio-${form_name}`, JSON.stringify(data));
        }, 5000);
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
            //On submit, fetch a new form
            if ('form_on_submit' in form_data.data) {
                load_new_form(form_data.data.form_on_submit, extra);
            }
            //On submit, go to new page
            if ('submit_endpoint' in form_data.data) {
                document.location.href = Flask.url_for(form_data.data['submit_endpoint'])
            }
            //delete local storage
            localStorage.removeItem(`Formio-${form_name}`)
        });
        // On cancel (button) go to new page
        formio.on('cancel', () => {
            if ('cancel_endpoint' in form_data.data) {
                if (confirm('Opgelet, de inhoud van dit formulier gaat verloren.  Bent u zeker?')) {
                    formio.resetValue();
                    localStorage.removeItem(`Formio-${form_name}`)
                    document.location.href = Flask.url_for(form_data.data['cancel_endpoint'])
                }
            }
        });
        formio.on('clear', () => {
            if (confirm('Opgelet, alle velden in dit formulier worden gewist.  Bent u zeker?')) {
                formio.resetValue();
            }
        });
    } else {
        alert(`Fout bij het ophalen van een form:\n ${form_data.data}`)
        document.location.reload();
    }
}