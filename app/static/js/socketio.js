class Socketio {
    receive_cbs = {}
    constructor() {
        this.socket = io();
        this.subscribe_on_receive("its-me-received", this.handle_its_me_received)
    }
    start() {
        this.socket.on('send_to_client', function (msg, cb) {
            if (msg.type in this.receive_cbs) {
                this.receive_cbs[msg.type](msg.type, msg.data);
            }
            if (cb)
                cb();
        }.bind(this));
        this.socket.on('connect', function () {
            this.socket.emit('its_me', {code: coworker.code});
        }.bind(this));

    }

    send_to_server(type, data) {
        this.socket.emit('send_to_server', {type: type, data: data});
        return false;
    }

    subscribe_on_receive(type, receive_cb) {
        this.receive_cbs[type] = receive_cb;
    }

    handle_its_me_received(type, data) {
        console.log("its-me-received: " + data);
    }

    subscribe_to_room(room_code) {
        this.socket.emit('subscribe_to_room', {room: room_code});
    }

}

var socketio
$(function () { // same as $(document).ready()
    socketio = new Socketio();
});
