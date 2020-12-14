from qt import *
from pyte import Screen, Stream, HistoryScreen, modes
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
            layout.add(self.text)

        set_font_options(self.text, {'setFamily': 'Courier New'})

        self.screen = Screen(columns, rows)
        self.stream = Stream(self.screen)

        self.position = 0
        self.sticky = True
        self.render_screen()

    @property
    def visible_lines(self):
        return self.text.height() // self.text.fontMetrics().lineSpacing() - 1
    
    @property
    def max_pos(self):
        return self.screen.cursor.y - self.visible_lines + 1

    def sizeHint(self) -> PySide2.QtCore.QSize:
        return QSize(600, 400)

    def resizeEvent(self, event: PySide2.QtGui.QResizeEvent):
        super().resizeEvent(event)
        
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
                    self.sticky = False

            elif event.angleDelta().y() < 0: # down
                if self.position < self.max_pos:
                    self.position += 1
                    if self.position == self.max_pos:
                        self.sticky = True

            self.render_screen()
            event.accept()
            return True

        return False

    def rx(self, string):
        self.stream.feed(string)
        self.render_screen()
        
    def render_screen(self):
        if self.sticky or self.position >= self.max_pos:
            self.position = self.max_pos

        if self.position < 0:
            self.position = 0
        
        lines = list(self.screen.buffer.keys())
        lines = lines[self.position:self.position + self.visible_lines]

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


        
class HistorySerialMonitorWidget(QWidget):
    tx = Signal(str)

    def __init__(self, *args, columns=120, rows=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text.verticalScrollBar().setDisabled(True);

        self.text.installEventFilter(self)
        self.installEventFilter(self)

        with CVBoxLayout(self) as layout:
            layout.add(self.text)

        set_font_options(self.text, {'setFamily': 'Courier New'})

        self.columns = columns

        self.screen = HistoryScreen(columns, self.visible_lines, history=1000, ratio=0.01)
        self.screen.set_mode(modes.LNM)
        self.stream = Stream(self.screen)

        self.render_screen()

    @property
    def visible_lines(self):
        return self.text.height() // self.text.fontMetrics().lineSpacing() - 1

    def sizeHint(self) -> PySide2.QtCore.QSize:
        return QSize(600, 400)

    def resizeEvent(self, event: PySide2.QtGui.QResizeEvent):
        super().resizeEvent(event)

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
                self.screen.prev_page()

            elif event.angleDelta().y() < 0: # down
                self.screen.next_page()

            self.render_screen()
            event.accept()
            return True

        return False

    def rx(self, string):
        self.stream.feed(string)
        self.render_screen()
        
    def render_screen(self):
        self.screen.resize(lines=self.visible_lines, columns=self.columns)

        print(
            'cursor x:', self.screen.cursor.x, 
            'x:', self.screen.cursor.y,
            'history.top:', len(self.screen.history.top),
            'history.bottom:', len(self.screen.history.bottom),
            
        )

        html = self.render_to_html(self.screen.buffer)
        self.text.setHtml(html)

    def render_to_html(self, buffer):
        html = []
        html.append('<body>')

        for line in buffer:
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