from qt import *
import typing
from style import colors
import re
import itertools


class Command(QAction):
    def __init__(self, text, parent=None, shortcut=None):
        super().__init__(text, parent)
        if shortcut:
            self.setShortcut(shortcut)
        CommandModel.commands.append(self)


class PopupDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prefix = ""
        self.normal = QPen('gray')
        self.contains = QPen('lightgray')
        self.highlight = QPen(QColor(colors.blue))

    def set_prefix(self, prefix):
        self.prefix = prefix

    def paint(self, 
            painter: PySide2.QtGui.QPainter, 
            option: PySide2.QtWidgets.QStyleOptionViewItem, 
            index: PySide2.QtCore.QModelIndex
        ):

        self.initStyleOption(option, index)
        prefix = self.prefix
        value = index.data(Qt.EditRole)
        shortcut = index.data(Qt.UserRole)

        # adjust full drawing area
        option.rect.setX(option.rect.x() + 5)
        option.rect.setWidth(option.rect.width() - 10)

        painter.save()

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QBrush('lightblue', Qt.SolidPattern))

        if prefix == "":
            painter.setPen(self.normal)
            painter.drawText(option.rect, Qt.AlignLeft, value)
        else:
            if prefix.lower() in value.lower():
                parts = re.split(prefix, value, flags=re.IGNORECASE)
                
                # the split is case insensitive, so use the lengths of the
                # parts to slice the original text out of the complete string
                sections = [parts[0]]
                length = len(parts[0])
                for part in parts[1:]:
                    sections.append(value[length:length + len(prefix)])
                    sections.append(part)
                    length += len(prefix) + len(part)

                prev = None
                rect = QRect(option.rect)
                for text in sections:
                    if text.lower() == prefix.lower():
                        painter.setPen(self.highlight)
                    else:
                        painter.setPen(self.contains)

                    if prev:
                        rect = QRect(prev.x() + prev.width(), prev.y(), option.rect.width(), prev.height())

                    prev = painter.drawText(rect, Qt.AlignLeft, text)
            else:
                painter.setPen(self.normal)
                painter.drawText(option.rect, Qt.AlignLeft, value)

        painter.setPen(self.normal)
        painter.drawText(option.rect, Qt.AlignRight, shortcut)

        painter.restore()


class CommandModel(QAbstractTableModel):
    commands = []
    sorted_commands = []

    def sort_commands(self, prefix):
        self.sorted_commands = [cmd for cmd in self.commands if prefix.lower() in cmd.text().lower()]
        self.sorted_commands.extend([cmd for cmd in self.commands if prefix.lower() not in cmd.text().lower()])

    def columnCount(self, parent: PySide2.QtCore.QModelIndex) -> int:
        return 1

    def rowCount(self, parent: PySide2.QtCore.QModelIndex) -> int:
        return len(self.commands)

    def data(self, index: PySide2.QtCore.QModelIndex, role: int) -> typing.Any:
        if not index.isValid():
            return None

        if role == Qt.EditRole:
            return self.sorted_commands[index.row()].text()
        
        elif role == Qt.UserRole:
            return self.sorted_commands[index.row()].shortcut().toString()

    def index(self, row: int, column: int, parent: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.QModelIndex:
        return self.createIndex(row, column)

    def get_command(self, pos):
        if type(pos) is QModelIndex:
            pos = pos.row()
        return self.sorted_commands[pos]


class CommandCompleter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.command_model = CommandModel(self)
        self.completion_list = QListView()
        self.completion_list.setUniformItemSizes(True)
        self.completion_list.setSelectionRectVisible(True)
        self.completion_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.completion_list.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.completion_list.setFixedHeight(500)
        self.completion_list.setModel(self.command_model)

        self.delegate = PopupDelegate(self)
        self.completion_list.setItemDelegate(self.delegate)

        self.completion_list.clicked.connect(lambda i: print('clicked', i))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.completion_list)
        self.active = False

        self.installEventFilter(self)
        self.completion_list.installEventFilter(self)

    def eventFilter(self, source, event):
        # if source is not self:
        #     print(source, event)
        #     print(self.completion_list.currentIndex())

        return False

    def open(self):
        self.active = True
        self.update_prefix('')
        
        index = self.completion_list.model().index(0, 0, QModelIndex())
        self.completion_list.setCurrentIndex(index)

        super().show()

    def close(self):
        self.active = False
        self.update_prefix('')
        super().hide()

    def update_prefix(self, prefix):
        self.delegate.set_prefix(prefix)
        self.command_model.sort_commands(prefix)

        index = self.completion_list.model().index(0, 0, QModelIndex())
        self.completion_list.setCurrentIndex(index)
        
        # redraw items in popup
        for row in range(self.completion_list.model().rowCount(QModelIndex())):
            index = self.completion_list.model().index(row, 0, QModelIndex())
            self.completion_list.update(index)

    def move_selection_up(self):
        current = self.completion_list.currentIndex()

        if current.row() > 0:
            new = self.completion_list.model().index(current.row() - 1, 0, QModelIndex())
            self.completion_list.setCurrentIndex(new)

    def move_selection_down(self):
        current = self.completion_list.currentIndex()

        if current.row() < self.completion_list.model().rowCount(QModelIndex()):
            new = self.completion_list.model().index(current.row() + 1, 0, QModelIndex())
            self.completion_list.setCurrentIndex(new)

    def get_selection(self):
        index = self.completion_list.currentIndex()
        return index.data(Qt.EditRole)

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
        
        self.setMinimumWidth(700)

        self.action = QAction("Command Palette", self)
        self.action.setShortcut('Ctrl+Shift+P')
        self.action.triggered.connect(self.palette)

        self.line = QLineEdit()
        self.command_completer = CommandCompleter(self)

        # self.line.returnPressed.connect(self.accept)
        self.line.textChanged.connect(self.command_completer.update_prefix)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.line)
        layout.addWidget(self.command_completer)

        self.command_completer.close()

        self.installEventFilter(self)
        self.line.installEventFilter(self)
        self.callback = lambda s: print(s)

    def palette(self):
        self.open()
        self.command_completer.open()

    def open(self, cb=None, prompt=None, placeholder=None, completer=None, validator=None, mask=None):
        if cb is None:
            self.callback = lambda s: print(s)
        else:
            self.callback = cb

        self.line.setText(prompt)
        self.line.setPlaceholderText(placeholder)
        self.line.setCompleter(completer)
        self.line.setValidator(validator)
        self.line.setInputMask(mask)

        self.center_on_parent()
        self.show()
        self.activateWindow()
        self.line.setFocus()

    def accept(self):
        if self.command_completer.active:
            result = self.command_completer.get_selection()
        else:
            result = self.line.text()

        if self.callback:
            self.callback(result)

        self.dismiss()

    def dismiss(self):
        self.callback = lambda s: print(s)
        self.line.clear()
        self.line.setPlaceholderText('')
        self.line.setCompleter(None)
        self.line.setValidator(None)
        self.line.setInputMask('')
        self.hide()
        self.command_completer.close()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if source is not self:
                
                if event.key() == Qt.Key_Return:
                    self.accept()

                if self.command_completer.active:
                    if event.key() == Qt.Key_Up:
                        event.accept()
                        self.command_completer.move_selection_up()
                        return True

                    elif event.key() == Qt.Key_Down:
                        event.accept()
                        self.command_completer.move_selection_down()
                        return True
            
            if event.key() == QtCore.Qt.Key_Escape:
                self.dismiss()
                event.accept()
                return True

        if event.type() == QEvent.WindowDeactivate:
            self.dismiss()
            event.accept()
            return True

        return False

    def center_on_parent(self):
        r = self.parent().frameGeometry()
        rect = QRect(r.x() - (self.width() / 2), r.y(), r.width(), 100)
        self.move(rect.center())


def CommandPalette(parent=None):
    if _CommandPalette._instance is None:
        _CommandPalette._instance = _CommandPalette(parent)

    return _CommandPalette._instance