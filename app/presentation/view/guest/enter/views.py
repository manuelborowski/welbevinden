from flask import redirect, render_template, request, url_for, jsonify, session, copy_current_request_context
import json
from . import enter
from app import log, socketio
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect

# @guest.route('/guest/<string:code>/<string:name>/<string:time>', methods=['POST', 'GET'])
@enter.route('/guest/enter', methods=['POST', 'GET'])
def show():
    print(request.args)
    config = {
        'check_server_endpoint': 'guest.enter.server_ajax_endpoint',
        'intro_video': "https://www.youtube.com/embed/YrLk4vdY28Q",
        'code': 'abcde',
        'first_name': 'manuel',
        'last_name': 'borowski',
        'email': 'emmanuel.borowski@gmail.com'
    }
    return render_template('guest/enter/enter.html', config=config, async_mode=socketio.async_mode)



@enter.route('/guest/enter/action/<string:jds>', methods=['GET', 'POST'])
def server_ajax_endpoint(jds):
    try:
        jd = json.loads(jds)
        if jd['action'] == 'get-timeout-1':
            return jsonify({"status": True})
    except Exception as e:
        log.error(f'execute action: {jd}')
        return jsonify({"status": False})

    return jsonify({"status": True})

# async connection to support chatboxes
@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.event
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.event
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room')
def on_close_room(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.event
def my_ping():
    emit('my_pong')


@socketio.event
def connect():
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app)



