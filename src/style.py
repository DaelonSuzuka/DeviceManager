from qt import *

from slickpicker import QColorEdit
import itertools

# palette_cache = QPalette()
# darkPalette = QPalette()
darkPalette = QStyleFactory.create('fusion').standardPalette()


light = QColor('#525252')
mid = QColor('#414141')
dark = QColor('#313131')
accent= QColor('#ca3e47')

class colors:
    navy = '#001f3f'
    blue = '#0074D9'
    aqua = '#7FDBFF'
    teal = '#39CCCC'
    olive = '#3D9970'
    green = '#2ECC40'
    lime = '#01FF70'
    yellow = '#FFDC00'
    orange = '#FF851B'
    red = '#FF4136'
    maroon = '#85144b'
    fuchsia = '#F012BE'
    purple = '#B10DC9'
    black = '#111111'
    gray = '#AAAAAA'
    silver = '#DDDDDD'
    white = '#FFFFFF'


# base
darkPalette.setColor(QPalette.WindowText, QColor(180, 180, 180))
darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
darkPalette.setColor(QPalette.Light, QColor(180, 180, 180))
darkPalette.setColor(QPalette.Midlight, QColor(90, 90, 90))
darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
darkPalette.setColor(QPalette.Text, QColor(180, 180, 180))
darkPalette.setColor(QPalette.BrightText, QColor(180, 180, 180))
darkPalette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
darkPalette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
darkPalette.setColor(QPalette.Link, QColor(56, 252, 196))
darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
darkPalette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))

# disabled
darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))


groups = [
    ('Normal', QPalette.Normal),
    ('Active', QPalette.Active),
    ('Inactive', QPalette.Inactive),
    ('Disabled', QPalette.Disabled),
]

roles = [
    ('Window', QPalette.Window),
    ('Background', QPalette.Background),
    ('WindowText', QPalette.WindowText),
    ('Foreground', QPalette.Foreground),
    ('Base', QPalette.Base),
    ('AlternateBase', QPalette.AlternateBase),
    ('ToolTipBase', QPalette.ToolTipBase),
    ('ToolTipText', QPalette.ToolTipText),
    ('PlaceholderText', QPalette.PlaceholderText),
    ('Text', QPalette.Text),
    ('Button', QPalette.Button),
    ('ButtonText', QPalette.ButtonText),
    ('BrightText', QPalette.BrightText),
    ('', QPalette.Base),
    ('Light', QPalette.Light),
    ('Midlight', QPalette.Midlight),
    ('Dark', QPalette.Dark),
    ('Mid', QPalette.Mid),
    ('Shadow', QPalette.Shadow),
    ('', QPalette.Base),
    ('Highlight', QPalette.Highlight),
    ('HighlightedText', QPalette.HighlightedText),
    ('', QPalette.Base),
    ('Link', QPalette.Link),
    ('LinkVisited', QPalette.LinkVisited),
]


ColorRole = Qt.UserRole + 1
SelectedRole = Qt.UserRole + 2


class Delegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        value = index.data(Qt.DisplayRole)
        color = index.data(ColorRole)
        selected = index.data(SelectedRole)

        painter.save()
        if value:
            r = option.rect
            rect = QRect(r.x() + 10, r.y(), r.width() - 10, r.height())
            painter.setPen(QPen('lightgray'))
            painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, value)

        elif color:
            path = QPainterPath()
            path.addRoundedRect(option.rect, 5, 5)
            painter.fillPath(path, color)
            
            if selected:
                painter.setPen(QPen(QColor(colors.white), 3))
                painter.drawRoundedRect(option.rect, 7, 7)

        painter.restore()


class PaletteItem(QTableWidgetItem):
    def __init__(self, text, role=None, group=None, color=None):
        super().__init__(text)
        if role and group and color:
            self.role = role
            self.group = group
            self.color = color
            self.set_color(color)
            self.setData(SelectedRole, False)
        
    def set_color(self, color):
        self.setData(ColorRole, color)
        self.setBackgroundColor(color)
        self.set_tooltip()

    def set_tooltip(self):
        self.setToolTip(f'{self.role[0]}: {self.group[0]} ({self.color})')

    def clicked(self):
        self.setData(SelectedRole, not self.data(SelectedRole))


class PaletteTable(QTableWidget):
    def __init__(self):
        super().__init__()
        
        self.setItemDelegate(Delegate())
        self.setColumnCount(5)
        self.setColumnWidth(0, 200)
        self.setRowCount(len(roles))
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.setHorizontalHeaderLabels(['Role', 'Normal', 'Active', 'Inactive', 'Disabled'])
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.itemClicked.connect(self.click)
        
    def click(self, item):
        item.clicked()

    def set_palette(self, palette):
        for i, role in enumerate(roles):
            item = PaletteItem(role[0])
            self.setItem(i, 0, item)

            for j, group in enumerate(groups, 1):
                item = PaletteItem('', role, group, palette.color(group[1], role[1]))
                self.setItem(i, j, item)

    def get_colors(self):
        palette_colors = []
        
        for row, col in itertools.product(range(self.rowCount()), range(1, self.columnCount())):
            item = self.item(row, col)
            palette_colors.append((item.group[1], item.role[1], item.color))

        return palette_colors
    
    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction(QAction('Clear Selection', menu, triggered=self.clear_selection))
        menu.exec_(event.globalPos())

    def clear_selection(self):
        for row, col in itertools.product(range(self.rowCount()), range(1, self.columnCount())):
            self.item(row, col).setData(SelectedRole, False)

    def get_selected_items(self):
        selected_items = []
        for row, col in itertools.product(range(self.rowCount()), range(1, self.columnCount())):
            item = self.item(row, col)
            if item.data(SelectedRole):
                selected_items.append(item)

        return selected_items


class PaletteEditor(QDialog):
    palette_updated = Signal(object)
    palette_reset = Signal()

    def __init__(self):
        super().__init__()

        self.table = PaletteTable()
        self.resize(650, 1000)

        self.color_edit = QColorEdit()
        self.set_color = QPushButton('Set Color')
        self.apply = QPushButton('Apply Palette')
        self.reset = QPushButton('Reset Palette')
        self.table.set_palette(darkPalette)
        
        self.table.itemDoubleClicked.connect(self.double_click)
        self.set_color.clicked.connect(self.set_clicked)
        self.apply.clicked.connect(self.apply_clicked)
        self.reset.clicked.connect(self.palette_reset)

        layout = QGridLayout()
        layout.addWidget(self.color_edit, 0, 0, 1, 1)
        layout.addWidget(self.set_color, 0, 1, 1, 1)
        layout.addWidget(self.apply, 0, 2, 1, 1)
        layout.addWidget(self.reset, 0, 3, 1, 1)
        layout.addWidget(self.table, 1, 0, 1, 4)
        self.setLayout(layout)

    def double_click(self, item):
        if hasattr(item, 'color'):
            self.color_edit.color = item.color
            self.color_edit.lineEdit.color = item.color

    def set_clicked(self):
        hex_color = self.color_edit.lineEdit.text()
        selected_items = self.table.get_selected_items()
        if selected_items:
            for item in selected_items:
                item.set_color(QColor(hex_color))
            self.table.viewport().update()

    def apply_clicked(self):
        colors = self.table.get_colors()

        # QApplication().instance().style().standardPalette()
        # QStyleFactory.create('fusion').standardPalette()
        # palette = QGuiApplication.palette()

        palette = QStyleFactory.create('fusion').standardPalette()
        for color in colors:
            palette.setColor(color[0], color[1], color[2])

        self.palette_updated.emit(palette)