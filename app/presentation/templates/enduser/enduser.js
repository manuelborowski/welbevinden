var stage_2_div = $(".stage-2")
var all_tabs = []
$(document).ready(function () {
    add_info_items($(".info-items-content"), items);

    // setInterval(function () {
    //     check_server();
    // }, 5000);

    $(".nav-link").on("click", function () {
        switch_to_tab($(this))
    });

    // debug
    // stage_2_div.show();
    socketio.subscribe_on_receive('stage-2-visible', control_stage_visibility_cb)
});

function control_stage_visibility_cb(type, data) {
    if(type === 'stage-2-visible') {
        if(data.show) {
                stage_2_div.show();
        } else {
                stage_2_div.hide();
        }
    }
}


function check_server() {
    var jd = {
        "action": "get-timeout-1",
        "code": config.code,
    };
    $.getJSON(Flask.url_for(config.check_server_endpoint, {'jds': JSON.stringify(jd)}),
        function (jd) {
            if (jd.status) {
                stage_2_div.show();
            } else {
            }
        });
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

function add_info_item(where, room_id, room_title) {
    var $item = $($(".info-item-template").clone().html());
    var $div_item = $("#CLB-div").find(".info-items-content");
    $div_item.append($item);
}


