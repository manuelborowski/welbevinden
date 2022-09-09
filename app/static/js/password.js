async function password_to_server(id, password, update_endpoint) {
    const ret = await fetch(Flask.url_for(update_endpoint), {
        headers: {'x-api-key': api_key,},
        method: 'POST',
        body: JSON.stringify({id, password}),
    });
    const status = await ret.json();
    if (status.status) {
        bootbox.alert(`Paswoord is aangepast`)
    } else {
        bootbox.alert(`Kan paswoord niet niet aanpassen: ${status.data}`)
    }
}

async function update_password(item, update_endpoint) {
    let person = get_data_of_row(item_ids[0]);

    init_popup(`Geef een nieuw paswoord voor ${person.voornaam} ${person.naam}`);

    const new_password = create_input_element('Nieuw paswoord', 'new-password', 'new-password', {size: 20});
    add_to_popup_body(new_password);
    const force_new_password = create_checkbox_element('Gebruiker moet paswoord veranderen bij aanloggen', 'foce-new-password', 'force-new-password');
    add_to_popup_body(force_new_password),
    show_popup();

    save_button_event(async function(event) {
        hide_popup();
        password_to_server(person.id, $("#new-password").val(), update_endpoint);
    });


    // bootbox.prompt({
    //     title: `Geef een nieuw paswoord voor ${person.voornaam} ${person.naam} <br> Of laat leeg om te wissen`,
    //     callback: result => {
    //         if (result !== null) {
    //             password_to_server(person.id, result, update_endpoint)
    //         }
    //     }
    // })
}

