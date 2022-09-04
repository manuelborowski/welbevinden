async function update_vsk_numbers(start) {
    const ret = await fetch(Flask.url_for('api.update_vsk_number'), {
        headers: {'x-api-key': api_key,},
        method: 'POST',
        body: JSON.stringify({start}),
    });
    const status = await ret.json();
    if (status.status) {
        bootbox.alert(`Er zijn ${status.data} nieuwe nummers toegekend`)
    } else {
        bootbox.alert(`Fout bij het toekennen van de nieuwe nummers: ${status.data}`)
    }
}

async function clear_vsk_numbers() {
    const ret = await fetch(Flask.url_for('api.clear_vsk_numbers'), {
        headers: {'x-api-key': api_key,},
        method: 'POST'
    });
    const status = await ret.json();
    if (status.status) {
        bootbox.alert(`Alle nummers (${status.data}) zijn gewist`)
    } else {
        bootbox.alert(`Fout bij het wissen van de nummers: ${status.data}`)
    }
}

async function new_vsk_numbers(item) {
    const ret = await fetch(Flask.url_for('api.get_last_vsk_number'), {headers: {'x-api-key': api_key,}})
    const data = await ret.json();
    if (data.status) {
        if (data.data === -1) { // no numbers yet
            bootbox.prompt({
                title: "Er zijn nog geen nummers toegekend. Geef het startnummer in",
                inputType: "number",
                callback: result => {
                    if (result) update_vsk_numbers(result)
                }
            })
        } else {
            const start = parseInt(data.data);
            bootbox.dialog({
                title: 'Vsk nummers toekennen',
                message: `<p>Het eerstvolgende nummer is ${start}</p>`,
                buttons: {
                    ok: {
                        label: 'Ok',
                        className: 'btn-success',
                        callback: function () {
                            update_vsk_numbers(start)
                        }
                    },
                    cancel: {
                        label: 'Annuleren',
                        className: 'btn-warning',
                        callback: function () {

                        }
                    },
                    clear_all: {
                        label: 'Alle Vsk nummers wissen',
                        className: 'btn-danger',
                        callback: function () {
                            clear_vsk_numbers()
                        }
                    },
                }
            })
        }
    } else {
        bootbox.alert(`Sorry, er is iets fout gegaan: ${data.data}`)
    }
}

subscribe_right_click('new-vsk-numbers', new_vsk_numbers);


const badge_raw2hex = code => {
    const decode_caps_lock = code => {
        let out = '';
        const dd = {
            '&': '1', 'É': '2', '"': '3', '\'': '4', '(': '5', '§': '6', 'È': '7', '!': '8', 'Ç': '9',
            'À': '0', 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F'
        };
        for (r of code) {
            out += dd[r.toUpperCase()];
        }
        return out
    }

    const process_int_code = code_int => {
        if (code_int < 100000 || code_int > parseInt('FFFFFFFF', 16)) {
            return {is_rfid_code: false, code: code_int}
        }
        //convert the int to a hex number, add leading 0's (if required) to get 8 characters
        //revert the order of the 4 tupples (big to little endian)
        let hex = code_int.toString(16).toUpperCase();
        hex = '0'.repeat(8 - hex.length) + hex;
        hex = hex.split('');
        let out = []
        for (let i = 6; i >= 0; i -= 2) {
            out = out.concat(hex.slice(i, i + 2))
        }
        out = out.join('');
        return {is_rfid_code: true, code: out}
    }

    let is_rfid_code = true
    let is_valid_code = true
    code = code.toUpperCase();

    if (code.length === 8) {
        // Asume a hex code of 8 chars
        if (code.contains('Q')) {
            // the badgereader is a qwerty HID device
            code = code.replace(/Q/g, 'A');
        }
        if (!/^[0-9a-fA-F]+$/.test(code)) {
            // it is not a valid hex code :-(  Check if capslock was on
            code = decode_caps_lock(code);
            if (!/^[0-9a-fA-F]+$/.test(code)) {
                // it is not a valid code :-(
                is_valid_code = is_rfid_code = false;
            }
        }
    } else {
        // Assume it is an integer code, so test it
        if (/^[0-9]+$/.test(code)) {
            const res = process_int_code(parseInt(code));
            is_rfid_code = res.is_rfid_code;
            code = res.code;
        } else {
            code = decode_caps_lock(code);
            if (/^[0-9]+$/.test(code)) {
                const res = process_int_code(parseInt(code));
                is_rfid_code = res.is_rfid_code;
                code = res.code;
            } else {
                is_valid_code = is_rfid_code = false;
            }
        }
    }
    console.log(is_rfid_code, code);
    return {valid: is_rfid_code, code}
}

async function check_rfid(item) {
    let student = get_data_of_row(item_ids[0]);
    bootbox.prompt({
        title: `Scan de badge van student ${student.voornaam} ${student.naam}`,
        callback: result => {
            if (result) {
                res = badge_raw2hex(result);
                if (res.valid) {
                    bootbox.dialog({
                        title: 'Nieuwe RFID code?',
                        message: `De gescande code is ${res.code}<br> De huidige code is ${student.rfid}`,
                        // callback: result => {console.log(result)},
                        buttons: {
                            ok: {
                                label: 'Gebruik nieuwe code',
                                className: 'btn-success',
                                callback: async function () {

                                    const ret = await fetch(Flask.url_for('api.update_student'), {
                                        headers: {'x-api-key': api_key,},
                                        method: 'POST',
                                        body: JSON.stringify({id: student.id, rfid: res.code}),
                                    });
                                    const status = await ret.json();
                                    if (status.status) {
                                        update_cell(item_ids[0], 'rfid', res.code);
                                    } else {
                                        bootbox.alert(`Kan de RFID code niet aanpassen: ${status.data}`)
                                    }
                                }
                            },
                            cancel: {
                                label: 'Annuleren',
                                className: 'btn-warning',
                                callback: function () {

                                }
                            },
                        }
                    })
                }
            }
        }
    })
}

subscribe_right_click('check-rfid', check_rfid);
