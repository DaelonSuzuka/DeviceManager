from .qt import *


class ContextLayout:
    def add(self, item, *args):
        if isinstance(item, QWidget):
            self.addWidget(item, *args)
        elif isinstance(item, QLayout):
            self.addLayout(item, *args)

        return item

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class CVBoxLayout(QVBoxLayout, ContextLayout):
    def __init__(self, parent=None, stretch=None, **kwargs):
        if parent is None or isinstance(parent, QWidget):
            super().__init__(parent, **kwargs)
        else:
            super().__init__(**kwargs)
            if stretch:
                parent.addLayout(self, stretch)
            else:
                parent.addLayout(self)


class CHBoxLayout(QHBoxLayout, ContextLayout):
    def __init__(self, parent=None, stretch=None, **kwargs):
        if parent is None or isinstance(parent, QWidget):
            super().__init__(parent, **kwargs)
        else:
            super().__init__(**kwargs)
            if stretch:
                parent.addLayout(self, stretch)
            else:
                parent.addLayout(self)


class CGridLayout(QGridLayout, ContextLayout):
    def __init__(self, parent=None, stretch=None, **kwargs):
        if parent is None or isinstance(parent, QWidget):
            super().__init__(parent, **kwargs)
        else:
            super().__init__(**kwargs)
            if stretch:
                parent.addLayout(self, stretch)
            else:
                parent.addLayout(self)


class VLine(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.VLine)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setLineWidth(1)


class HLine(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setLineWidth(1)