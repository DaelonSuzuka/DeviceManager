from .qt import *


class ContextLayout:
    def __init__(self, parent=None, stretch=None, margins=None, **kwargs):
        if parent is None or isinstance(parent, QWidget):
            super().__init__(parent, **kwargs)
        else:
            super().__init__(**kwargs)
            if stretch:
                parent.addLayout(self, stretch)
            else:
                parent.addLayout(self)

        if margins:
            self.setContentsMargins(*margins)

        self._stack = []
        self.next_layout = None

    @property
    def _layout(self):
        layout = self
        if len(self._stack) > 0:
            layout = self._stack[len(self._stack) - 1]
        return layout

    def __call__(self):
        return self._layout

    def add(self, item, *args, **kwargs):
        if isinstance(item, QWidget):
            self._layout.addWidget(item, *args, **kwargs)
        elif isinstance(item, QLayout):
            self._layout.addLayout(item, *args, **kwargs)
        elif isinstance(item, list):
            for i in item:
                self._layout.add(i, *args, **kwargs)

        return item

    def vbox(self, *args, **kwargs):
        self.next_layout = CVBoxLayout(self._layout, *args, **kwargs)
        return self

    def hbox(self, *args, **kwargs):
        self.next_layout = CHBoxLayout(self._layout, *args, **kwargs)
        return self

    def __enter__(self):
        if self.next_layout is not None:
            self._stack.append(self.next_layout)
            self.next_layout = None
        return self

    def __exit__(self, type, value, traceback):
        if len(self._stack) > 0:
            self._stack.pop()


class CVBoxLayout(ContextLayout, QVBoxLayout):
    pass


class CHBoxLayout(ContextLayout, QHBoxLayout):
    pass


class CGridLayout(ContextLayout, QGridLayout):
    pass


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