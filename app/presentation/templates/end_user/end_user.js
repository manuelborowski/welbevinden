var stage_2_div = $(".stage-2")
var is_coworker = floors.includes(user.profile);
var $coworker_content;
$(document).ready(function () {
    add_info_items($(".info-items-content"), items);

    $(".nav-link").on("click", function () {
        switch_to_tab($(this))
    });

    socketio.subscribe_on_receive('stage-2-visible', control_stage_visibility_cb)

    if(is_coworker) {
        $coworker_content = add_tab(user.profile + "-medewerker");
    }
    chat.start(user.code, add_chat_room_cb, delete_chat_room_cb);
    socketio.subscribe_on_receive('stage-show-time', set_stage_show_time_cb)
});


function control_stage_visibility_cb(type, data) {
    if(type === 'stage-2-visible') {
        if(data.show) { stage_2_div.show(); } else { stage_2_div.hide(); }
    }
}


function switch_to_tab(tab_this) {
    console.log(tab_this);
    $(".nav-link").removeClass('active');
    tab_this.addClass('active');

    var div_array = tab_this[0].id.split("-");
    div_array.pop();
    div_array.push("div");
    var div_id = div_array.join("-");
    $(".nav-divs").hide();
    $("#" + div_id).show()
}

function add_tab(name) {
    var $nav_item = $($('.nav-item-template').clone().html());
    $("#nav-bar").append($nav_item);
    $nav_item.children(".nav-link").attr("id", name + "-tab");
    $nav_item.children(".nav-link").text(name);
    $(".nav-link").on("click", function () {switch_to_tab($(this))});
    var $nav_div = $($('.nav-div-template').clone().html());
    $("#nav-bar").after($nav_div);
    $nav_div.attr("id", name + "-div");
    return $nav_div.children(".row")
}

function add_chat_room(where, room_id, room_title) {
    var $chat_room = $($('.chat_window_template').clone().html());
    where.append($chat_room);
    $chat_room.attr("id", room_id)
    $chat_room.attr("id", room_id)
    $chat_room.children().children(".top_menu").children(".title").text(room_title)
}


$(function () {
});

function add_chat_room_cb(floor, code, title) {
    if (is_coworker) {
        add_chat_room($coworker_content, code, title);
        chat.subscribe_to_room(user.profile, code, user.code, user.initials);
    }
    $chat_room_location = $("#" + floor + "-div").children(".row")
    add_chat_room($chat_room_location, code, title);
    chat.subscribe_to_room(user.profile, code, user.code, user.initials);
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
