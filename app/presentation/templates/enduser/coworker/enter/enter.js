var $div_content

$(function () {
    $div_content = add_tab(coworker.profile + "-medewerker");
    chat.start(coworker.code, add_chat_room_cb, delete_chat_room_cb);
    socketio.subscribe_on_receive('stage-show-time', set_stage_show_time_cb)
});

function add_chat_room_cb(floor, code, title) {
    console.log("add chatroom " + floor + " " + code + " " + title)
    add_chat_room($div_content, code, title);
    chat.subscribe_to_room(coworker.profile, code, coworker.code, coworker.initials);
}

function delete_chat_room_cb(room_code) {}

// Called by server to set the time when a stage needs to be displayed.
// It is up to the client to inform the server that a stage needs to be displayed
function set_stage_show_time_cb(type, data) {
    var now = new Date();
    var stage = data["stage"];
    var show_time = new Date(data["show-time"]);
    var delta = show_time - now;
    if (delta < 0) {delta = 0;}
    setTimeout(stage_show_time_cb, delta, stage);
}


//Called when timeout occurs.  The server is informed of the timeout and will subsequently inform the client to
//show a stage
function stage_show_time_cb(stage) {
    socketio.send_to_server('stage-show-time', {stage: stage});
}
