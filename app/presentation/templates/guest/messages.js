var formio_form
$(document).ready(function () {


    const form_options = {
        sanitizeConfig: {
            addTags: ['iframe'],
            addAttr: ['allow'],
            ALLOWED_TAGS: ['iframe'],
            ALLOWED_ATTR: ['allow']
        },
    }
    Formio.createForm(document.getElementById('response-form'), response_form, form_options).then((form) => {
        $.each(defaults, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error ) {
                console.log("skipped ", k, v);
            }
        });
        formio_form = form
    });
});
