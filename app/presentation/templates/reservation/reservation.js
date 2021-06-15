$(document).ready(function () {
    const table = document.querySelector('#table');
    function return_entry(id, label, value) {
        return template = `<tr>
                <td class="noborder">${label}</td>
                <td class="noborder"><input id="${id}" name="${id}" type="text" value="${value}" size="100"></td>
            </tr>`
    }

    form_details.fields.forEach(item => {
        const label = form_details.config[item].label;
        const value = form_details.config[item].default;
        table.innerHTML += return_entry(item, label, value);
    });
});