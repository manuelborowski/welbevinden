var $div_content

$(function () {
    // $div_content = add_tab(coworker.profile + "-medewerker");
    chat.start(guest.code, add_chat_room_cb, delete_chat_room_cb);
});

function add_chat_room_cb(floor, code, title) {
    console.log("add chatroom " + floor + " " + code + " " + title)
    $chat_room_location = $("#" + floor + "-div").children(".row")
    add_chat_room($chat_room_location, code, title);
    chat.subscribe_to_room(guest.profile, code, guest.code);
}

function delete_chat_room_cb(room_code) {}