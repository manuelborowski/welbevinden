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
        // const a = [{label: "drie", value: 3}, {label: "vier", value: 4}]
        // const a = ["drie","vier"]
        // form.getComponent("select-leerling").setItems(a, false)
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
        const select_leerling_id = form.getComponent("select-leerling").id;
        const select_leerling = document.querySelector("#" + select_leerling_id + " select")
        select_leerling.addEventListener("change", e => {
            console.log(e);
            const school = e.detail.value.split("-")[3];
            _form.getComponent('bs-welke-secundaire-school').value = school;
            _form.getComponent('ss-andere-basisschool').value = school;
        })
    });
}

const get_choices = (values, id) => {
    console.log(values, id)
    return data.select_choices[id]
    // return [{value: 1, label:"een"}, {value: 2, label: "twee"}]
}