var this_form
$(document).ready(function () {
    Formio.createForm(document.getElementById('register-form'), registration_form).then((form) => {
        // $.each(default_settings, function (k, v) {
        //     form.getComponent(k).setValue(v);
        // });
        this_form = form
        form.on('change', form_changed);
        // form.on('change', function (changed) {
        //     console.log('changed');
        //     var key = changed.changed.component.key;
        //     if (key.includes('select-boxes-')) {
        //         var val = changed.changed.value;
        //         var select_components = form.getComponent('select-period-boxes').components;
        //         select_components.forEach(function (item, index) {
        //             item.setValue(0);
        //         });
        //         form.getComponent(key).setValue(val);
        //     }
        // });
    });
});


function form_changed(changed) {
    console.log('changed');
    this_form.off('change', form_changed);
    var key = changed.changed.component.key;
    if (key.includes('select-boxes-')) {
        var val = changed.changed.value;
        var select_components = this_form.getComponent('select-period-boxes').components;
        select_components.forEach(function (item, index) {
            item.setValue(0);
        });
        this_form.getComponent(key).setValue(val);
        setTimeout(function (){this_form.on('change', form_changed)}, 1000);
    }
}


