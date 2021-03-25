from qt import *
from main_window import MainWindow
from style import darkPalette
import qtawesome as qta
import logging

from codex import DeviceManager
from networking import DiscoveryService
from networking import DeviceClient, DeviceServer


class Application(BaseApplication):
    t = QElapsedTimer()

    def __init__(self) -> None:
        # turn on high dpi scaling - must be done before creating app
        # self.setAttribute(Qt.AA_EnableHighDpiScaling, True)

        super().__init__()

        self.init_app_info()
        self.init_app_style()

        # instantiate application systems
        self.device_manager = DeviceManager(self)
        self.discovery = DiscoveryService(self)
        self.server = DeviceServer(self)
        self.client = DeviceClient(self)

        # create window
        self.window = MainWindow()
        self.window.show()

    def init_app_info(self):
        self.setOrganizationName("LDG Electronics")
        self.setOrganizationDomain("LDG Electronics")
        self.setApplicationName("Device Manager")
        self.setApplicationVersion("v0.1")

    def init_app_style(self):
        self.setStyle('Fusion')
        self.setPalette(darkPalette)
        self.setWindowIcon(qta.icon('mdi.card-text-outline'))
        set_font_options(self, {'setPointSize': 10})

    # def notify(self, receiver, event):
    #     self.t.start()
    #     ret = QApplication.notify(self, receiver, event)
    #     if(self.t.elapsed() > 10):
    #         logging.getLogger('performance').warning(
    #             f"processing event type {event.type()} for object {receiver.objectName()} " 
    #             f"took {self.t.elapsed()}ms"
    #         )
    #     return ret