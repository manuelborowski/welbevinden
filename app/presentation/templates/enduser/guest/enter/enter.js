var $div_content

$(function () {
    // $div_content = add_tab(coworker.profile + "-medewerker");
    chat.start(guest.code, add_chat_room_cb, delete_chat_room_cb);
    socketio.subscribe_on_receive('stage-show-time', set_stage_show_time_cb)
});

function add_chat_room_cb(floor, code, title) {
    console.log("add chatroom " + floor + " " + code + " " + title)
    $chat_room_location = $("#" + floor + "-div").children(".row")
    add_chat_room($chat_room_location, code, title);
    chat.subscribe_to_room(guest.profile, code, guest.code);
}

function delete_chat_room_cb(room_code) {}

function set_stage_show_time_cb(type, data) {
    console.log(type);
    console.log(data["show-time"]);
    var now = new Date();
    var stage = data["stage"];
    var show_time = new Date(data["show-time"]);
    var delta = show_time - now;
    if (delta < 0) {delta = 0;}
    setTimeout(stage_show_time_cb, delta, stage);
}

function stage_show_time_cb(stage) {
    var now = new Date();
    console.log("timeout " + stage + " " + now );
    socketio.send_to_server('stage-show-time', {stage: stage});
}