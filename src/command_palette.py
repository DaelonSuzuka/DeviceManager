from qt import *


class CommandCompleter(QCompleter):
    def __init__(self):
        super().__init__()

        self.setMaxVisibleItems(10)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)

        font = self.popup().font()
        font.setPointSize(16)
        self.popup().setFont(font)


class CommandPaletteLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()

        font = self.font()
        font.setPointSize(16)
        self.setFont(font)


class _CommandPalette(QDialog):
    _instance = None

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('CommandPalette')
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setMinimumWidth(500)

        self.action = QAction("Command Palette", self)
        self.action.setShortcut('Ctrl+Shift+P')
        self.action.triggered.connect(self.open)

        self.command_completer = CommandCompleter()
        self.line = CommandPaletteLineEdit()
        self.line.setCompleter(self.command_completer)
        self.line.returnPressed.connect(self.accept)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line)
        self.setLayout(layout)

        self.installEventFilter(self)
        self.callback = None

    def open(self, cb=None, prompt=None, placeholder=None, completer=None):
        if prompt:
            pass
        if placeholder:
            self.line.setPlaceholderText(placeholder)
        if completer:
            self.line.setCompleter(completer)
        if cb:
            self.callback = cb

        self.show()
        self.activateWindow()
        self.line.setFocus()

    def accept(self):
        result = self.line.text()
        if self.callback:
            self.callback(result)
        self.dismiss()

    def dismiss(self):
        self.line.clear()
        self.line.setPlaceholderText('')
        self.line.setCompleter(self.command_completer)
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.dismiss()

    def eventFilter(self, source, event):
        if event.type() == QEvent.WindowDeactivate:
            self.dismiss()
        return super().eventFilter(source, event)

    def center(self):
        r = self.parent().frameGeometry()
        rect = QRect(r.x() - 250, r.y(), r.width(), 100)
        self.move(rect.center())

    def register_action(self):
        print('register')


def CommandPalette(parent=None):
    if _CommandPalette._instance is None:
        _CommandPalette._instance = _CommandPalette(parent)

    return _CommandPalette._instance