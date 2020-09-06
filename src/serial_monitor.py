from qt import *
from pyte import Screen, Stream
from style import colors


key_map = {
    Qt.Key_Up: '\033[A',
    Qt.Key_Down: '\033[B',
    Qt.Key_Right: '\033[C',
    Qt.Key_Left: '\033[D',
    Qt.Key_Home: '\033[1~',
    Qt.Key_End: '\033[OF',
    Qt.Key_PageUp: '\033[5~',
    Qt.Key_PageDown: '\033[6~',
    Qt.Key_F1: '\033OP',
    Qt.Key_F2: '\033OQ',
    Qt.Key_F3: '\033OR',
    Qt.Key_F4: '\033OS',
    Qt.Key_F5: '\033[16~',
    Qt.Key_F6: '\033[17~',
    Qt.Key_F7: '\033[18~',
    Qt.Key_F8: '\033[19~',
    Qt.Key_F9: '\033[20~',
    Qt.Key_F10: '\033[21~',
    Qt.Key_F11: '\033[22~',
    Qt.Key_F12: '\033[24~',
}


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


class SerialMonitorWidget(QWidget):
    tx = Signal(str)

    def __init__(self, *args, columns=120, rows=1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text.verticalScrollBar().setDisabled(True);

        self.text.installEventFilter(self)
        self.installEventFilter(self)

        with CVBoxLayout(self) as layout:
            layout.addWidget(self.text)

        font = self.text.font()
        font.setFamily('Courier New')
        self.text.setFont(font)
        
        self.screen = Screen(columns, rows)
        self.stream = Stream(self.screen)

        self.position = 0
        self.visible_lines = self.text.height() // self.text.fontMetrics().lineSpacing()

        self.render_screen()

    def sizeHint(self) -> PySide2.QtCore.QSize:
        return QSize(600, 400)

    def resizeEvent(self, event: PySide2.QtGui.QResizeEvent):
        super().resizeEvent(event)

        self.visible_lines = self.text.height() // self.text.fontMetrics().lineSpacing()
        self.render_screen()

    def eventFilter(self, watched: PySide2.QtCore.QObject, event: PySide2.QtCore.QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            key = event.text()

            if event.key() in key_map:
                key = key_map[event.key()]

            self.tx.emit(key)
            event.accept()
            return True
        elif event.type() == QEvent.Type.Wheel:
            if event.angleDelta().y() > 0: # up
                if self.position > 0:
                    self.position -= 1
                    self.render_screen()

            elif event.angleDelta().y() < 0: # down
                if self.position < len(self.screen.buffer):
                    self.position += 1
                    self.render_screen()
                
            event.accept()
            return True

        return False

    @property
    def max_pos(self):
        return len(self.screen.buffer) - self.visible_lines

    def rx(self, string):
        sticky = True
        if self.max_pos >= 0:
            if self.position != self.max_pos:
                sticky = False

        self.stream.feed(string)
        self.render_screen(sticky)
        
    def render_screen(self, sticky=False):
        if sticky or self.position > self.max_pos:
            self.position = self.max_pos

        if self.position < 0:
            self.position = 0
        
        lines = list(self.screen.buffer.keys())
        lines = lines[self.position:self.position + self.visible_lines]

        print('screen:', self.position, 'cursor:', self.screen.cursor.y, 'length:', len(self.screen.buffer), 'max_pos:', len(self.screen.buffer) - self.visible_lines, 'sticky:', sticky)

        html = self.render_to_html(self.screen.buffer, lines)
        self.text.setHtml(html)

    def render_to_html(self, buffer, lines):
        html = []
        html.append('<body>')

        for line in lines:
            text = ''
            for _, char in buffer[line].items():

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