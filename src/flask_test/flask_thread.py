from flask import Flask, render_template
from flask_socketio import SocketIO

from qt import *


class FlaskThread(QThread):
    def __init__(self):
        super().__init__()
        app = Flask(__name__)
        socketio = SocketIO(app)
        self.app = app
        self.socketio = socketio

        @app.route('/')
        @app.route('/index')
        def index():
            return render_template('index.html')


        @socketio.on('message')
        def message_handler(json, methods=['GET', 'POST']):

            print('received my event: ' + str(json))

            socketio.emit('message', json)

    def __del__(self):
        self.wait()

    def run(self):
        self.socketio.run(self.app)