var socket;
var rooms = {}
$(function () { // same as $(document).ready()
    socket = io();

    socket.on('connect', function () {
        socket.emit('its_me', {code: coworker.code});
    });

    socket.on('send_to_client', function (msg, cb) {
        if (msg.type === "chat-line") {
            var room_code = msg.data.room;
            var text = msg.data.text;
            var sender_code = msg.data.sender
            receive_chat_line_from_server(room_code, sender_code, text);
        } else if (msg.type === "its-me-received") {
            console.log("its-me-received: " + msg.data);
        }
        if (cb)
            cb();
    });
});


function Message(arg) {
    this.text = arg.text;
    this.message_side = arg.message_side;
    this.messages = arg.messages
    this.draw = function (_this) {
        return function () {
            var $message = $($('.message_template').clone().html());
            $message.addClass(_this.message_side).find('.text').html(_this.text);
            _this.messages.append($message);
            return setTimeout(function () {
                $message.addClass('appeared');
                return _this.messages.animate({scrollTop: _this.messages.prop('scrollHeight')}, 300);
            }, 0);
        };
    }(this);
    return this;
}


function subscribe_to_room(floor_level, room_code, sender_code, room_history) {
    socket.emit('subscribe_to_room', {room: room_code});
    rooms[room_code] = {
        floor_level: floor_level,
        sender_code: sender_code,
        jq_send_button: $("#" + room_code).children(".chat_window").children(".bottom_wrapper").children(".send_message"),
        jq_input_text: $("#" + room_code).children(".chat_window").children(".bottom_wrapper").children(".message_input_wrapper").children(".message_input"),
        jq_output_messages: $("#" + room_code).children(".chat_window").children(".messages")
    };

    rooms[room_code].jq_send_button.on("click", {value: room_code}, function (e) {
        var room = e.data.value;
        return send_chat_line_to_server(room, rooms[room].sender_code, rooms[room].jq_input_text);
    });

    rooms[room_code].jq_input_text.on("keyup", {value: room_code}, function (e) {
        if (e.which === 13) {
            var room = e.data.value;
            return send_chat_line_to_server(room, rooms[room].sender_code, rooms[room].jq_input_text);
        }
    });

    $.each(room_history, function(i, v) {
        receive_chat_line_from_server(room_code, v.owner_code, v.text);
    });
}

function send_chat_line_to_server(room_code, sender_code, $jq_input_element=null, text=null) {
    if ($jq_input_element) {
        text = $jq_input_element.val();
        $jq_input_element.val("");
    }
    if (text.trim() === "") return;
    socket.emit('send_to_server', {type: "chat-line", data: {room: room_code, sender: sender_code, text: text}});
    return false;
}

function receive_chat_line_from_server(room_code, sender_code, text) {
    var message = new Message({
        text: text,
        message_side: room_code == sender_code ? 'left' : 'right',
        messages: rooms[room_code].jq_output_messages
    });
    message.draw();
}