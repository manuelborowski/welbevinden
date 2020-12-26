var rooms = {}
$(function () { // same as $(document).ready()
    socketio.subscribe_on_receive("chat-line", receive_chat_line_from_server);
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
    socketio.subscribe_to_room(room_code);
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
}

function send_chat_line_to_server(room_code, sender_code, $jq_input_element=null, text=null) {
    if ($jq_input_element) {
        text = $jq_input_element.val();
        $jq_input_element.val("");
    }
    if (text.trim() === "") return;
    socketio.send_to_server('chat-line',{room: room_code, sender: sender_code, text: text});
    return false;
}

function receive_chat_line_from_server(type, data) {
    var message = new Message({
        text: data.text,
        message_side: data.room == data.sender ? 'left' : 'right',
        messages: rooms[data.room].jq_output_messages
    });
    message.draw();
}