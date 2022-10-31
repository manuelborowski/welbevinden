var _form = null;
$(document).ready(function () {
    load_formio_form();
});


const load_formio_form = async () => {
    Formio.createForm(document.getElementById('survey-form'), data.template).then((form) => {
        _form = form
        $.each(data.default, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error) {
                return;
            }
        });
        form.on('submit', async function(submission) {
            const ret = await fetch(Flask.url_for('survey.save'), {method: 'POST', body: JSON.stringify(submission.data), });
            const status = await ret.json();
            if (status.status) {
                window.location.href = Flask.url_for('survey.done') + `?targetgroup=${status.data.targetgroup}&status=${status.data.status}&message=${status.data.message}`
            } else {
                bootbox.alert(`Er is een fout opgetreden:<br> ${status.data}`)
            }
        })
        const select_leerling_component = form.getComponent("select-leerling");
        if (select_leerling_component) {
            const select_leerling = document.querySelector("#" + select_leerling_component.id + " select")
            select_leerling.addEventListener("change", e => {
                const school = e.detail.value.split("+")[3];
                var component = _form.getComponent('bs-welke-secundaire-school');
                if (component)  component.setValue(school);
                component = _form.getComponent('select-basisschool');
                if (component) {
                    component.setValue(school);
                    component.redraw();
                }
            })
        }
    });
}
