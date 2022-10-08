var _form = null;
$(document).ready(function () {
    load_formio_form();
});


const load_formio_form = async () => {
    Formio.createForm(document.getElementById('survey-form'), data.template).then((form) => {
        _form = form
        var button_id; // hack to set the value of the button, which was just clicked, to false again.
        $.each(data.default, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error) {
                return;
            }
        });
        form.on('submit', async function(submission) {
            const ret = await fetch(Flask.url_for('survey.done'), {method: 'POST', body: JSON.stringify(submission.data), });
            const status = await ret.json();
            if (status.status) {
                bootbox.alert(`Er zijn ${status.data} nieuwe nummers toegekend`)
            } else {
                bootbox.alert(`Fout bij het toekennen van de nieuwe nummers: ${status.data}`)
            }
            _form.getComponentById(button_id).setValue(false);
        })
    });
}
