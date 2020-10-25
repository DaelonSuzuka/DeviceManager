from qt import *
import json


class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.results = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})
        self.header = set_font_options(QTextEdit(''), {'setFamily': 'Courier New'})
        
        self.save = QPushButton('Save')
        self.load = QPushButton('Load')

        with CVBoxLayout(self) as layout:
            layout.add(QPushButton('1'))
            layout.add(QPushButton('2'))
            with layout.hbox() as layout:
                with layout.vbox() as layout:
                    layout.add(QPushButton('3'))
                    layout.add(QPushButton('4'))
                with layout.vbox() as layout:
                    layout.add(QPushButton('5'))
                    layout.add(QPushButton('6'))