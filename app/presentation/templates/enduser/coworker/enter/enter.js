$(function () {
    subscribe_to_room(coworker.code, receive_message);

    send_to_server(coworker.code, coworker.code, "test message");
});

function receive_message(room_code, sender_code, message) {
    console.log(room_code, sender_code, message);
}