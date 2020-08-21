from qt import *
from devices import SerialDevice, DeviceWidget
from pyte import HistoryScreen, Screen, Stream
from serial import SerialException
from style import colors

class NullBuffer:
    def __init__(self):
        self.buffer = ""

    def reset(self):
        self.buffer = ""

    def insert_char(self, c):
        self.buffer += c

    def completed(self):
        if self.buffer:
            return True 
        return False


class SerialMonitor(SerialDevice):
    profile_name = "SerialMonitor"

    def __init__(self, port=None, baud=115200, device=None):
        super().__init__(port=port, baud=baud, device=device)

        self.msg = NullBuffer()
        self.message_tree = None
        self.w = None

    def recieve(self, string):
        """ do something when a complete string is captured in self.communicate() """
        self.log.debug(f"RX: {string}")
        self.base_signals.send.emit(string)
        
    def communicate(self):
        """ Handle comms with the serial port. Call this often, from an event loop or something. """
        if not self.active:
            return

        # serial transmit
        try:
            if not self.queue.empty():
                self.ser.write(self.queue.get().encode())
        except SerialException as e:
            self.log.exception(e)

        # serial recieve
        try:
            while self.ser.in_waiting:
                self.msg.insert_char(self.ser.read(1).decode())
        except Exception as e:
            name = ''
            if hasattr(self, 'profile_name'):
                name = self.profile_name
                
            self.log.exception(f"{name}: {self.port} | {e}")

        # handle completed message
        if self.msg.completed():
            msg = self.msg.buffer
            self.recieve(msg)
            self.msg.reset()

    @property
    def widget(self):
        if self.w is None:
            self.w = SerialMonitorDockWidget(self.title, self.guid)
            self.connect_monitor(self.w.monitor)
        
        return self.w


fg_map = {
    "black": "black",
    "red": colors.red,
    "green": colors.green,
    "brown": "brown",
    "blue": colors.blue,
    "magenta": "magenta",
    "cyan": colors.teal,
    "white": colors.gray,
    "default": colors.gray,  # white.
}

bg_map = {
    "black": '#313131',
    "red": colors.red,
    "green": colors.green,
    "brown": "brown",
    "blue": colors.blue,
    "magenta": "magenta",
    "cyan": colors.teal,
    "white": colors.gray,
    "default": '#313131'  # black.
}


def render_to_html(buffer):
    html = [f'<body style="background-color:{bg_map["default"]};">']

    for _, chars in buffer.items():
        text = ''
        for _, char in chars.items():

            text += f'<span style="color:{fg_map[char.fg]}; background-color:{bg_map[char.bg]};">'
            text += char.data
            text += '</span>'

        text += '<br>'
        html.append(text)

    html.append('</body>')
    return "\n".join(html)


class SerialMonitorWidget(QTextEdit):
    tx = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        
        self.screen = Screen(120, 20)
        self.stream = Stream(self.screen)

        html = render_to_html(self.screen.buffer)
        self.setHtml(html)

    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        key = event.text()

        if event.key() == Qt.Key_Up:
            print('up')
            key = '\e[A'
        if event.key() == Qt.Key_Down:
            print('down')
            key = '\e[B'
        if event.key() == Qt.Key_Left:
            print('left')
            key = '\e[C'
        if event.key() == Qt.Key_Right:
            print('right')
            key = '\e[D'


        self.tx.emit(key)

    def rx(self, string):
        self.stream.feed(string)

        html = render_to_html(self.screen.buffer)
        self.setHtml(html)


class SerialMonitorDockWidget(DeviceWidget):
    def build_layout(self):
        grid = QGridLayout()
        
        self.monitor = SerialMonitorWidget()
        grid.addWidget(self.monitor)

        self.setWidget(QWidget(layout=grid))
