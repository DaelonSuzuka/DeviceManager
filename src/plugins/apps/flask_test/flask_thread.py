from flask import Flask, render_template
from urllib.parse import urlparse
from qt import *
from devices import SubscriptionManager


# disable flask logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


shared_devices = {}

class FlaskWorker(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        self.app = Flask(__name__)

        @self.app.route('/')
        @self.app.route('/index')
        def index():
            return render_template('index.html')

        @self.app.route('/devices')
        def devices():
            print(shared_devices)
            devices = [f'{t}' for d, t in shared_devices.items()]
            return render_template('devices.html', devices=devices)

        self.app.run(debug=True, use_reloader=False)


@SubscriptionManager.subscribe
class FlaskApp_(QWidget):
    tab_name = 'Flask'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.server = QWebSocketServer('flask', QWebSocketServer.NonSecureMode)
        self.server.newConnection.connect(self.on_new_connection)
        self.sockets = []

        if self.server.listen(address=QHostAddress.Any, port=5001):
            print(f"Device server listening at: {self.server.serverAddress().toString()}:{str(self.server.serverPort())}")
        else:
            print('Failed to start device server.')

        self.thread = QThread()
        self.worker = FlaskWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

        # self.web_view = QWebEngineView()
        # self.web_view.load(QUrl('http://localhost:5000'))

        self.text = QTextEdit()
        self.button = QPushButton()
        self.button.clicked.connect(lambda: self.processTextMessage('beep'))

        with CVBoxLayout(self) as layout:
            with layout.hbox() as layout:
                layout.add(self.button)
            layout.add(QLabel('Qt text widget:'))
            layout.add(self.text)
            layout.add(QLabel('Web view:'))
            # layout.add(self.web_view)

    def on_new_connection(self):
        socket = self.server.nextPendingConnection()
        self.sockets.append(socket)
        
        url = urlparse(socket.resourceName())
        print(url)

        socket.textMessageReceived.connect(self.processTextMessage)
        socket.disconnected.connect(lambda: print("socket disconnected"))
        
    def processTextMessage(self, message):
        self.text.append(message)
        self.send_later(message)

    def send_later(self, message):
        for socket in self.sockets:
            QTimer.singleShot(10, lambda: socket.sendTextMessage(message))

    def device_added(self, device):
        shared_devices[device.guid] = device.title