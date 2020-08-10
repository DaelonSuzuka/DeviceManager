import json
from qt import *
import typing


class Line(QHBoxLayout):
    def __init__(self, text=""):
        super().__init__()

        self.line = QLineEdit(text)
        self.add = QPushButton('+')
        self.add.setFixedSize(20, 20)
        self.remove = QPushButton('-')
        self.remove.setFixedSize(20, 20)

        self.addWidget(self.line)
        self.addWidget(self.add)
        self.addWidget(self.remove)


class MultiLineEdit(QVBoxLayout):
    def __init__(self, items=[]):
        super().__init__()
        self.setSpacing(5)

        self.lines = []

        if items:
            self.add_items(items)

    def add_items(self, items):
        for row, item in enumerate(items):
            self.add_item(item, row)

    def add_item(self, item, row):
        line = Line(str(item))
        self.lines.append(line)
        line.add.clicked.connect(self.add_row)
        # line.remove.clicked.connect(lambda row=row, line=line: self.remove_row(line))

        self.addLayout(line)

    def add_row(self):
        self.add_item("", len(self.lines))

    def remove_row(self, line):
        print('remove:', line)
        # self.lines[row].deleteLater()

    def get_lines(self):
        return [item.line.text() for item in self.lines]


class Field:
    def __init__(self, name:str, default, objtype, doc:str=None) -> None:
        # write to __dict__ to bypass __setattr__
        self.__dict__['name'] = name
        self.__dict__['default'] = default
        self.__dict__['type'] = objtype
        self.value = None
        self.__doc__ = doc

    def get(self):
        if self.value != None:
            return self.value
        else: 
            return self.default

    def __call__(self):
        return self.get()

    def __bool__(self):
        return bool(self.get())

    def __contains__(self, key):
        return key in self.get()

    def __eq__(self, other):
        return self.get() == other

    def __str__(self) -> str:
        return str(self.get())

    def __repr__(self):
        return f'{self.name}: {self.get()}'

    def __setattr__(self, name, value) -> None:
        if name in ['default', 'type', 'name']:
            raise AttributeError("'{}' attribute cannot be changed after Field creation".format(name))
        else:
            self.__dict__[name] = value

    def done(self, new_value):
        if new_value != self.get():
            self.value = new_value

    def get_widget(self):
        if self.type == bool:
            widget = QCheckBox(checked=self.get())
            widget.done = lambda: self.done(widget.isChecked())
        elif self.type == typing.List[str]:
            widget = MultiLineEdit(items=self.get())
            widget.done = lambda: self.done(widget.get_lines())
        elif self.type == str:
            widget = QLineEdit(text=str(self.get()))
            widget.done = lambda: self.done(widget.text())
        elif self.type == int:
            widget = QLineEdit(text=str(self.get()))
            widget.done = lambda: self.done(int(widget.text()))
        else:
            widget = QLabel('wat')
            widget.done = lambda: print(self.name)

        return widget


class Settings:
    def __init__(self) -> None:
        self.__dict__['fields'] = {}
        for name in dir(self.__class__):
            if name not in dir(Settings) and not name.startswith('__'):
                self.fields[name] = Field(name, getattr(self, name), self.__annotations__[name])
                delattr(self.__class__, name)

    def __getattr__(self, name):
        if name in self.fields:
            return self.fields[name]

    def __setattr__(self, name, value) -> None:
        if name in self.fields:
            self.__dict__['fields'][name].value = value
            SettingsManager().save_now()

    def __repr__(self) -> str:
        items = {
            name: field()
            for name, field in self.fields.items()
        }
        return repr(items)

    def to_json(self):
        return {
            field.name: field.get()
            for _, field in self.fields.items()
            if field.value != None
        }

    def register(self, name):
        SettingsManager().register(name, self)
        return self


class _SettingsManager:
    _instance = None

    def __init__(self):
        self.sections = {}
        self.settings = {}
        
        self.load_file()

    def load_file(self):
        try:
            with open('settings.json') as f:
                self.settings = json.load(f)
                Field.on_update = self.schedule_save
        except FileNotFoundError:
            pass

    def register(self, name, section):
        self.sections[name] = section

        if name in self.settings:
            for field, value in self.settings[name].items():
                setattr(section, field, value)
    
    def show_dialog(self):
        self.dialog = SettingsDialog(self.sections)
        result = self.dialog.exec_()

    def schedule_save(self):
        self.save_now()

    def save_now(self):
        s = repr({k:v.to_json() for k, v in self.sections.items() if v.to_json() != {}})
        s = s.replace("'", '"').replace('False', 'false').replace('True', 'true')

        try:
            s2 = json.dumps(json.loads(s), indent=4)
            with open('settings.json', 'w') as f:
                f.write(s2)
        except json.JSONDecodeError as e:
            print(e)
            print('json load/dump failed!')
            print(s)


def SettingsManager():
    if _SettingsManager._instance is None:
        _SettingsManager._instance = _SettingsManager()

    return _SettingsManager._instance


class SettingsDialog(QDialog):
    def __init__(self, sections, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setMinimumSize(500, 500)
        
        self.setStyleSheet("""
            QGroupBox { font: 20px}
            QLabel { font: 20px}
            QPushButton { font: 20px}
            QLineEdit { font: 20px}
            QTabBar { font: 20px}
        """)
        
        self.accepted.connect(self.accept)
        # self.rejected.connect(lambda: print('rejected'))

        self.field_widgets = []
        self.tabs = QTabWidget()        

        for name, section in sections.items():
            form = QFormLayout()
            form.setSpacing(20)
            form.setMargin(10)
            for _, field in section.fields.items():     
                w = field.get_widget()
                self.field_widgets.append(w)
                form.addRow(field.name, w)

            self.tabs.addTab(QWidget(layout=form), name)

        hbox = QHBoxLayout(alignment=Qt.AlignRight)
        hbox.addWidget(QPushButton('Ok', clicked=self.ok_clicked))
        hbox.addWidget(QPushButton('Cancel', clicked=self.cancel_clicked))
        hbox.addWidget(QPushButton('Apply', clicked=self.apply_clicked))

        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def ok_clicked(self):
        self.accept()
        self.hide()

    def cancel_clicked(self):
        self.reject()

    def apply_clicked(self):
        self.accepted.emit()

    def accept(self):
        for widget in self.field_widgets:
            widget.done()
        SettingsManager().save_now()