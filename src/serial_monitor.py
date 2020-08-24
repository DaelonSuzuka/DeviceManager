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
    html = []
    html.append('<body>')

    for _, chars in buffer.items():
        text = ''
        for _, char in chars.items():

            # background and highlighting in chitin use the 'reverse' text attribute instead of setting the bg-color
            if char.reverse:
                text += f'<span style="color: {colors.black}; background-color: {fg_map[char.fg]}">'
            else:
                text += f'<span style="color: {fg_map[char.fg]};">'

            if char.data == ' ':
                text += '&nbsp;' # html collapses multiple spaces but not the nbsp character
            else:
                text += char.data
            text += '</span>'

        text += '<br>'
        html.append(text)

    html.append('</body>')
    return "\n".join(html)


class SerialMonitorWidget(QWidget):
    tx = Signal(str)

    def __init__(self, *args, columns=120, rows=30, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = QTextEdit()
        self.text.setReadOnly(True)

        with CVBoxLayout(self) as layout:
            layout.addWidget(self.text)

        font = self.text.font()
        font.setFamily('Courier New')
        self.text.setFont(font)
        
        self.screen = Screen(columns, rows)
        self.stream = Stream(self.screen)

        html = render_to_html(self.screen.buffer)
        self.text.setHtml(html)

    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        key = event.text()

        esc = '\033'
        key_map = {
            Qt.Key_Up: '[A',
            Qt.Key_Down: '[B',
            Qt.Key_Right: '[C',
            Qt.Key_Left: '[D',
            Qt.Key_Home: '[1~',
            Qt.Key_End: '[OF',
            Qt.Key_PageUp: '[5~',
            Qt.Key_PageDown: '[6~',
            Qt.Key_F1: 'OP',
            Qt.Key_F2: 'OQ',
            Qt.Key_F3: 'OR',
            Qt.Key_F4: 'OS',
            Qt.Key_F5: '[16~',
            Qt.Key_F6: '[17~',
            Qt.Key_F7: '[18~',
            Qt.Key_F8: '[19~',
            Qt.Key_F9: '[20~',
            Qt.Key_F10: '[21~',
            Qt.Key_F11: '[22~',
            Qt.Key_F12: '[24~',
        }

        if event.key() in key_map:
            key = esc + key_map[event.key()]

        self.tx.emit(key)

    def rx(self, string):
        self.stream.feed(string)

        html = render_to_html(self.screen.buffer)
        self.text.setHtml(html)
