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


