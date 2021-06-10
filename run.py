from app import flask_app, socketio

if __name__ == '__main__':
    socketio.run(flask_app, port=flask_app.config['FLASK_PORT'], host='127.0.0.1')

