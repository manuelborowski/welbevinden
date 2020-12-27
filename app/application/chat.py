from app.application import room as mroom
from app.application import socketio as msocketio


# received a chat line for a room.  Store the line and transmit to all clients with said room
def chat_line_received_cb(msg, client_sid=None):
    mroom.add_chat_line(msg['data']['room'], msg['data']['sender'], msg['data']['text'])
    msocketio.send_to_room(msg, msg['data']['room'])


msocketio.subscribe_on_type('chat-line', chat_line_received_cb)
