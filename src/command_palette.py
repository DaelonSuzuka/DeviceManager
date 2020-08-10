from qt import *
import typing


class Command(QAction):
    def __init__(self, text, parent=None, shortcut=None):
        super().__init__(text, parent)
        if shortcut:
            self.setShortcut(shortcut)
        CommandModel.commands.append(self)


class PopupDelegate(QStyledItemDelegate):
    def paint(  self, 
                painter: PySide2.QtGui.QPainter, 
                option: PySide2.QtWidgets.QStyleOptionViewItem, 
                index: PySide2.QtCore.QModelIndex
        ):

        self.initStyleOption(option, index)
        value = index.data(Qt.EditRole)

        painter.save()
        painter.setPen(QPen('lightgray'))
        painter.drawText(option.rect, Qt.AlignLeft, value)
        painter.restore()


class CommandModel(QAbstractItemModel):
    commands = []

    def columnCount(self, parent: PySide2.QtCore.QModelIndex) -> int:
        return 2

    def rowCount(self, parent: PySide2.QtCore.QModelIndex) -> int:
        return len(self.commands)

    def data(self, index: PySide2.QtCore.QModelIndex, role: int) -> typing.Any:
        if not index.isValid():
            return None

        if role == Qt.EditRole:
            col = index.column()
            if col == 0:
                return self.commands[index.row()].text()
            if col == 1:
                return self.commands[index.row()].shortcut().toString()

    def index(self, row: int, column: int, parent: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.QModelIndex:
        return self.createIndex(row, column)


class CommandCompleter(QCompleter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMaxVisibleItems(10)
        self.setCompletionMode(QCompleter.PopupCompletion)
        # self.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)

        self.command_model = CommandModel(self)
        self.setModel(self.command_model)

        self.delegate = PopupDelegate()
        self.default_popup = self.popup()

        self.command_popup = QTableView()
        self.command_popup.setColumnWidth(0, 300)
        self.command_popup.setColumnWidth(0, 300)


        self.setPopup(self.command_popup)
        self.popup().setItemDelegate(self.delegate)

        font = self.popup().font()
        font.setPointSize(16)
        self.popup().setFont(font)


class _CommandPalette(QDialog):
    _instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('CommandPalette')
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.StrongFocus)
        
        font = self.font()
        font.setPointSize(16)
        self.setFont(font)
        
        self.setMinimumWidth(500)

        self.action = QAction("Command Palette", self)
        self.action.setShortcut('Ctrl+Shift+P')
        self.action.triggered.connect(self.open)

        self.commands = [
            Command('Device Client: Connect', self, shortcut='Ctrl+Shift+C'),
            Command('Device Client: Disconnect', self, shortcut='Ctrl+Shift+D'),
            Command('Device Client: Set Address', self, shortcut='Ctrl+Shift+A'),
        ]

        self.command_completer = CommandCompleter(self)
        self.line = QLineEdit()
        self.line.setCompleter(self.command_completer)
        self.line.returnPressed.connect(self.accept)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line)
        self.setLayout(layout)

        self.installEventFilter(self)
        self.callback = lambda s: print(s)

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