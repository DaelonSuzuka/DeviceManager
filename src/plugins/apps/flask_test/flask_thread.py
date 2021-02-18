from flask import Flask, render_template
from flask_socketio import SocketIO

from qt import *





class FlaskWorker(QObject):
    message_recieved = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        app = Flask(__name__)
        socketio = SocketIO(app)
        self.app = app
        self.socketio = socketio

        @app.route('/')
        @app.route('/index')
        def index():
            return render_template('index.html')

        @socketio.on('message')
        def message_handler(msg, methods=['GET', 'POST']):
            print('rx:', str(msg))
            socketio.emit('message', msg)
            self.message_recieved.emit(str(msg))

        @socketio.on('connect')
        def connect(sid, env, auth):
            print('connected')


    def run(self):
        print('starting flask server')
        self.socketio.run(self.app, debug=True, use_reloader=False)


class FlaskApp(QWidget):
    tab_name = 'Flask'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.flask_thread = QThread()
        self.flask_worker = FlaskWorker()

        self.flask_worker.moveToThread(self.flask_thread)
        
        self.flask_thread.started.connect(self.flask_worker.run)
        self.flask_worker.message_recieved.connect(lambda s: self.text.append(s))

        self.flask_thread.start()

        self.web_view = QWebEngineView()
        self.web_view.load(QUrl('http://localhost:5000'))

        self.button = QPushButton()
        self.text = QTextEdit()

        with CVBoxLayout(self) as layout:
            layout.add(self.button)
            layout.add(self.text)
            layout.add(self.web_view)