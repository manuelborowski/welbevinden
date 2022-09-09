async function password_to_server2(id, password_data, update_endpoint) {
    const ret = await fetch(Flask.url_for(update_endpoint), {
        headers: {'x-api-key': api_key,},
        method: 'POST',
        body: JSON.stringify({id, password_data}),
    });
    const status = await ret.json();
    if (status.status) {
        bootbox.alert(`Paswoord is aangepast`)
    } else {
        bootbox.alert(`Kan paswoord niet niet aanpassen: ${status.data}`)
    }
}


const popup_callback = (action, opaque, data=null) => {
    if (action === 'submit') {
        const pwd_data = {
            password: data['new-password'],
            must_update: data['user-must-update-password']
        }
        password_to_server2(opaque.person.id, pwd_data, opaque.update_endpoint);
    }
}


async function update_password2(item, update_endpoint, popup) {
    let person = get_data_of_row(item_ids[0]);
    create_formio_popup(popup, {'new-password-user-name': `${person.voornaam} ${person.naam}`}, popup_callback, {person, update_endpoint})
}

