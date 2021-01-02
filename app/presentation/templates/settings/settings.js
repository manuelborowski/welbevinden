$(document).ready(function () {
    Formio.createForm(document.getElementById('stage-settings'), stage_settings_form).then((form) => {
        $.each(default_stage_settings, function (k, v){
            form.getComponent(k).setValue(v);
        });
        form.on('change', function (changed) {
            console.log("change " + changed);
        });
    });
});
