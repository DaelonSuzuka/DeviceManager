from qt import *
from pyte import HistoryScreen, Screen, Stream
from style import colors


fg_map = {
    "black": "black",
    "red": colors.red,
    "green": colors.green,
    "brown": "brown",
    "blue": colors.blue,
    "magenta": "magenta",
    "cyan": colors.teal,
    "white": colors.gray,
    "default": colors.gray,
}

bg_map = {
    "black": '#2a2a2a',
    "red": colors.red,
    "green": colors.green,
    "brown": "brown",
    "blue": colors.blue,
    "magenta": "magenta",
    "cyan": colors.teal,
    "white": colors.gray,
    "default": '#2a2a2a',
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
        
        self.screen = Screen(120, 30)
        self.stream = Stream(self.screen)

        html = render_to_html(self.screen.buffer)
        self.setHtml(html)

    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        key = event.text()

        if event.key() == Qt.Key_Up:
            print('up')
            key = '\eA'
        if event.key() == Qt.Key_Down:
            print('down')
            key = '\eB'
        if event.key() == Qt.Key_Left:
            print('left')
            key = '\eC'
        if event.key() == Qt.Key_Right:
            print('right')
            key = '\eD'


        self.tx.emit(key)

    def rx(self, string):
        self.stream.feed(string)

        html = render_to_html(self.screen.buffer)
        self.setHtml(html)
