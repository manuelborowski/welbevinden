var $div_content

$(function () {
    $div_content = add_tab(coworker.profile + "-medewerker");
    chat.start(add_chat_room_cb, delete_chat_room_cb);
});

function add_chat_room_cb(code, title) {
    console.log("add chatroom " + code + " " + title)
    add_chat_room($div_content, code, title);
    chat.subscribe_to_room(coworker.profile, code, coworker.code);
}

function delete_chat_room_cb(room_code) {}