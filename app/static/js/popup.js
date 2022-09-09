const popup_body = document.querySelector('#popup .modal-body');

const init_popup = (title, save_button=true, cancel_button=true, ok_button=false) => {
    document.querySelector('#popup .modal-title').innerHTML = title;
    popup_body.replaceChildren();
    const popup_footer = document.querySelector('#popup .modal-footer');
    popup_footer.replaceChildren();
    popup_footer.innerHTML = ''
    if (cancel_button) {popup_footer.innerHTML += '<button type="button" class="btn btn-secondary" data-dismiss = "modal">Annuleer</button>'}
    if (ok_button) {popup_footer.innerHTML += '<button type="button" class="btn btn-secondary" data-dismiss = "modal">Ok</button>'}
    if (save_button) {popup_footer.innerHTML += '<button type="button" class="btn btn-primary">Bewaren</button>'}
}

const hide_popup = () => {
    $('#popup').modal("hide");
}


const show_popup = () => {
    $('#popup').modal();
}

const save_button_event = cb => {
    document.querySelector('#popup .btn-primary').addEventListener('click', cb);
}

const add_to_popup_body = child => {
    popup_body.appendChild(child)
}

const create_select_element = (label, id, name, options, attributes={}) => {
    const div_element = document.createElement('div');
    div_element.classList.add('popup-div')
    const label_element = document.createElement('label');
    label_element.innerHTML = label;
    label_element.htmlFor = id;
    const select_element = document.createElement('select');
    select_element.name = name;
    select_element.id = id;
    for (const [k, v] of Object.entries(attributes)) {select_element.setAttribute(k, v);}
    select_element.size = 1;
    options_html = ''
    options.forEach(([v, l]) => {
        options_html += `<option value="${v}">${l}</option>`
    })
    select_element.innerHTML = options_html;
    div_element.appendChild(label_element);
    div_element.appendChild(document.createElement('br'));
    div_element.appendChild(select_element);
    return div_element;
}


const create_input_element = (label, id, name, attributes={}) => {
    const div_element = document.createElement('div');
    div_element.classList.add('popup-div')
    const label_element = document.createElement('label');
    label_element.innerHTML = label;
    label_element.htmlFor = id;
    const input_element = document.createElement('input');
    input_element.name = name;
    input_element.id = id;
    for (const [k, v] of Object.entries(attributes)) {input_element.setAttribute(k, v);}
    div_element.appendChild(label_element);
    div_element.appendChild(input_element);
    return div_element;
}


const create_checkbox_element = (label, id, name, attributes={}) => {
    const div_element = document.createElement('div');
    div_element.classList.add('popup-div')
    const label_element = document.createElement('label');
    label_element.innerHTML = label;
    label_element.htmlFor = id;
    const input_element = document.createElement('input');
    input_element.name = name;
    input_element.type = "checkbox";
    input_element.id = id;
    for (const [k, v] of Object.entries(attributes)) {input_element.setAttribute(k, v);}
    div_element.appendChild(label_element);
    div_element.appendChild(input_element);
    return div_element;
}


const create_p_element = (text) => {
    const p_element = document.createElement('p');
    p_element.innerHTML = text;
    return p_element
}