from .qt import *


class Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_widgets()
        self.connect_signals()
        self.build_layout()

    def create_widgets(self):
        pass

    def connect_signals(self):
        pass

    def build_layout(self):
        pass


class PersistentTabWidget(QTabWidget):
    def __init__(self, name, tabs=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        if tabs:
            for tab in tabs:
                if hasattr(tab, 'tab_name'):
                    self.addTab(tab, tab.tab_name)
            self.restore_state()
        self.currentChanged.connect(lambda i: QSettings().setValue(self.name, i))

    def restore_state(self):
        i = min(QSettings().value(self.name, 0), self.count())
        self.setCurrentIndex(i)


class PersistentCheckBox(QCheckBox):
    def __init__(self, name, changed=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

        prev_state = QSettings().value(self.name, 0)
        if prev_state == int(Qt.Checked):
            self.setCheckState(Qt.Checked)
        elif prev_state == int(Qt.PartiallyChecked):
            self.setCheckState(Qt.PartiallyChecked)

        if changed:
            self.stateChanged.connect(changed)

        self.stateChanged.connect(lambda: QSettings().setValue(self.name, self.checkState()))


class StateButton(QPushButton):
    state_changed = Signal(int)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if self._state != state:
            self._state = state
            self.state_changed.emit(self._state)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(60, 60))
        self.icons = []
        self._state = None
        
        self.clicked.connect(self.next_state)
        self.state_changed.connect(self.update_icon)

    def next_state(self):
        self.state = (self.state + 1) % len(self.icons)

    def update_icon(self):
        if self.icons:
            self.setIcon(self.icons[self.state])


class IconToggleButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(60, 60))
        self.setCheckable(True)

        self.icon_unchecked = QIcon()
        self.icon_checked = QIcon()

        self.clicked.connect(self.update_icon)

    def update_icon(self):
        if self.isChecked():
            self.setIcon(self.icon_checked)
        else:
            self.setIcon(self.icon_unchecked)


class ConfirmToggleButton(QPushButton):
    _state_changed = Signal(int)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if self._state != state:
            self._state = state
            self.timer.stop()
            self._state_changed.emit(self._state)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(50, 50))
        self.icons = []

        self._state = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.uncheck)
        self.timeout_time = 1000

        self.clicked.connect(self.next_state)
        self._state_changed.connect(self.update_icon)

    def uncheck(self):
        self.state = 0
        self.setChecked(False)
        self.setCheckable(False)

    def confirm(self):
        self.state = 1
        self.timer.start(self.timeout_time)

    def check(self):
        self.state = 2
        self.setCheckable(True)
        self.setChecked(True)

    def next_state(self):
        if self.state == 0:
            self.confirm()
        elif self.state == 1:
            self.check()
        elif self.state == 2:
            self.uncheck()

    def update_icon(self):
        if self.icons:
            self.setIcon(self.icons[self.state])
