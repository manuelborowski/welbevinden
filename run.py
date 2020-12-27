# -*- coding: utf-8 -*-
# run.py

import os

from app import flask_app, socketio

if __name__ == '__main__':

    # flask_app.run(**app_options)
    socketio.run(flask_app, port=5120, host='127.0.0.1')