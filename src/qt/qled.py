from .qt import *

class QLed(QWidget):
    def __init__(self, color=None):

        self.ledIcon = QLabel()
        self.ledIcon.setObjectName('ledIcon')

        self.changeColor(color)

        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.ledIcon)

        self.ledIcon.setAlignment(Qt.AlignHCenter)
        self.ledIcon.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0, 0, 0, 0)

    def changeColor(self, color):

        pixmap = QPixmap('img/offLED.png')
        if color == "blue":
            pixmap = QPixmap('img/blueLED.png')
        if color == "green":
            pixmap = QPixmap('img/greenLED.png')
        if color == "red":
            pixmap = QPixmap('img/redLED.png')
        pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio)

        self.ledIcon.setPixmap(pixmap)

        
class LedBargraph(QWidget):
    def __init__(self, color='red', number=8):
        super().__init__()
        layout = QHBoxLayout()

        self.on_color = color
        self.number = number

        self.leds = []
        for i in range(number):
            led = QLed(color=color)
            self.leds.append(led)
            layout.addWidget(led)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

    def update(self, value):
        bits = reversed([int(n) for n in bin(value)[2:].zfill(self.number)])

        for i, bit in enumerate(bits):
            self.leds[i].changeColor(self.on_color if bit else 'off')