from qt import *
from main_window import MainWindow
from style import darkPalette
import qtawesome as qta
import logging


class Application(QApplication):
    t = QElapsedTimer()

    def __init__(self) -> None:
        # turn on high dpi scaling - must be done before creating app
        # self.setAttribute(Qt.AA_EnableHighDpiScaling, True)

        super().__init__()
        
        # org information
        self.setOrganizationName("LDG Electronics")
        self.setOrganizationDomain("LDG Electronics")
        self.setApplicationName("Device Manager")
        self.setApplicationVersion("v0.1")

        self.default_palette = QGuiApplication.palette()
        self.setStyle('Fusion')
        self.setPalette(darkPalette)
        self.setWindowIcon(qta.icon('mdi.card-text-outline'))
        
        set_font_options(self, {'setPointSize': 10})

        self.window = MainWindow()
        self.window.show()

    # def notify(self, receiver, event):
    #     self.t.start()
    #     ret = QApplication.notify(self, receiver, event)
    #     if(self.t.elapsed() > 10):
    #         logging.getLogger('performance').warning(
    #             f"processing event type {event.type()} for object {receiver.objectName()} " 
    #             f"took {self.t.elapsed()}ms"
    #         )
    #     return ret