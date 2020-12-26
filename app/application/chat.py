from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from app import flask_app, socketio
from app.application import room as mroom, enduser as menduser
import datetime

@socketio.event
def subscribe_to_room(message):
    join_room(message['room'])


@socketio.event
def leave_room(message):
    leave_room(message['room'])


@socketio.on
def close_room(message):
    close_room(message['room'])


@socketio.event
def send_to_server(msg):
    if msg['type'] == 'chat-line':
        mroom.add_chat_line(msg['data']['room'], msg['data']['sender'], msg['data']['text'])
        emit('send_to_client', msg, room=msg['data']['room'])


@socketio.on('disconnect')
def disconnect_socket():
    menduser.remove_socketio_sid(request.sid)


@socketio.event
def connect():

    pass


@socketio.event
def its_me(data):
    menduser.set_socketio_sid(data['code'], request.sid)
    emit('send_to_client', {'type' : 'its-me-received', 'data' : True}, room=request.sid)
    history = mroom.get_history(data['code'])
    for chat_line in history:
        msg = {
            'type': 'chat-line',
            'data' : chat_line
        }
        emit('send_to_client', msg, room=request.sid)
