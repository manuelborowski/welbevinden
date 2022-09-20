async function server_database_integrity_check(endpoint, databases) {
    busy_indication_on();
    const ret = await fetch(Flask.url_for(endpoint), {
        headers: {'x-api-key': api_key,},
        method: 'POST',
        body: JSON.stringify({databases}),
    });
    const status = await ret.json();
    busy_indication_off();
    console.log(status);
    formio_popup_set_value('log-check-integrity', status.data);
}


const database_popup_callback = (action, opaque, data=null) => {
    if (action === 'event-start-integrity-check') {
        console.log(action, opaque, data);
        var databases = []
        if (data['check-ad']) databases.push('ad');
        server_database_integrity_check(opaque, databases)
    }
}


async function database_integrity_check(item, endpoint, popup) {
    await formio_popup_create(popup, {}, database_popup_callback, endpoint, '1500px');
    await formio_popup_subscribe_event('event-start-integrity-check', database_popup_callback, endpoint);

}

