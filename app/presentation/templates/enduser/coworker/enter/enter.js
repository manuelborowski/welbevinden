var $div_content

$(function () {
    $div_content = add_tab(coworker.profile + "-medewerker");
    chat.start(coworker.code, add_chat_room_cb, delete_chat_room_cb);
});

function add_chat_room_cb(floor, code, title) {
    console.log("add chatroom " + floor + " " + code + " " + title)
    add_chat_room($div_content, code, title);
    chat.subscribe_to_room(coworker.profile, code, coworker.code, coworker.initials);
}

function delete_chat_room_cb(room_code) {}