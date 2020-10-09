#!/usr/bin/env python3

from qt import *
from main_window import MainWindow
from style import darkPalette
import sys
import signal
import logging
from log_monitor import log_handler
import qtawesome as qta


class MyApplication(QApplication):
    t = QElapsedTimer()

    def __init__(self) -> None:
        # turn on high dpi scaling - must be done before creating app
        # self.setAttribute(Qt.AA_EnableHighDpiScaling, True)

        super().__init__()
        
        self.setOrganizationName("LDG Electronics")
        self.setOrganizationDomain("LDG Electronics")
        self.setApplicationName("Device Manager")
        self.setApplicationVersion("v0.1")

        self.default_palette = QGuiApplication.palette()
        self.setStyle('Fusion')
        self.setPalette(darkPalette)
        self.setWindowIcon(qta.icon('mdi.card-text-outline'))
        
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)

        # configure logging
        logging.basicConfig(filename='log.txt', level=logging.DEBUG)
        # add loghandler to redirect logs into the LogMonitor widget
        logging.getLogger().addHandler(log_handler)

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


def run():
    # Create the Qt Application
    app = MyApplication()

    def ctrlc_handler(sig, frame):
        app.window.close()
        app.shutdown()

    # grab the keyboard interrupt signal 
    signal.signal(signal.SIGINT, ctrlc_handler)

    # Run the main Qt loop
    result = app.exec_()
    
    sys.exit(result)

if __name__ == "__main__":
    run()