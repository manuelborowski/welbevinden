$(document).ready(function () {
    const table = document.querySelector('#table');
    function return_entry(label, id) {
        return template = `<tr><td>${label}</td><td><input id="${id}" name="${id}" type="text" value="" size="100"></td></tr>`
    }

    form_details.forEach(item => {
        console.log(return_entry(item[0], item[1]));
        table.innerHTML += return_entry(item[0], item[1]);
    });
});