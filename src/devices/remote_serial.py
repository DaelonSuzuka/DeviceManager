from qt import *

class RemoteSerial:
    def __init__(self, port=None, timeout=0):
        self.port = port
        self.read_buffer = ""

        self.socket = QWebSocket()
        self.socket.textMessageReceived.connect(self.recieve)        
        # self.socket.disconnected.connect(lambda: print("disconnected"))

        if self.port:
            self.open()

    def open(self):
        self.socket.open(QUrl(self.port))

    def close(self):
        self.socket.close()

    def write(self, string):
        self.socket.sendTextMessage(string.decode())

    def recieve(self, string):
        self.read_buffer += string

    def read(self, number=1):
        result = ""
        for i in range(number):
            result += self.read_buffer[:1]
            self.read_buffer = self.read_buffer[1:]
        return result.encode()

    @property
    def in_waiting(self):
        return len(self.read_buffer)