function flash_messages(list) {
    for (var i = 0; i < list.length; i++) {
        var message = list[i];
        bootbox.alert(message);
    }
}

function busy_indication_on() {
    document.getElementsByClassName("busy-indicator")[0].style.display = "block";
}

function busy_indication_off() {
    document.getElementsByClassName("busy-indicator")[0].style.display = "none";
}

$(document).ready(function () {
   document.querySelector(".navbar-nav").addEventListener("click", e => {
       console.log(e);
       const link_elements = document.querySelectorAll(".nav-link");
       link_elements.forEach(link => {
           link.classList.remove("navbar-selected")
       });

       e.target.classList.add("navbar-selected");
   })

    const page = window.location.pathname.split('/')[1];
    const nav_element = document.querySelector(`#${page}`);
    nav_element.classList.add("navbar-selected");
    console.log(page)
});