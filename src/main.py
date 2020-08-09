#!/usr/bin/env python3

from qt import *
from main_window import MainWindow
from style import darkPalette, PaletteEditor
import sys
import signal
import logging
from log_monitor import log_handler
from settings import SettingsManager


class MyApplication(QApplication):
    t = QElapsedTimer()

    def __init__(self) -> None:
        super().__init__()
        self.default_palette = QGuiApplication.palette()
        self.setStyle('Fusion')
        self.setPalette(darkPalette)

        self.settings_manager = SettingsManager()

        # configure logging
        logging.basicConfig(filename='log.txt', level=logging.DEBUG)
        # add loghandler to redirect logs into the LogMonitor widget
        logging.getLogger().addHandler(log_handler)

        self.window = MainWindow()
        self.window.show()

        # self.palette_editor = PaletteEditor()
        # self.palette_editor.setPalette(darkPalette)
        # self.palette_editor.show()
        # self.palette_editor.palette_updated.connect(self.update_palette)
        # self.palette_editor.palette_reset.connect(self.reset_palette)

    def update_palette(self, palette):
        self.setPalette(palette)
        
        QPixmapCache().clear()
        self.relaunch_window()

    def reset_palette(self):
        QPixmapCache().clear()
        self.setPalette(self.default_palette)
        self.window.setPalette(self.default_palette)
        self.relaunch_window()

    def relaunch_window(self):
        self.window.close()
        self.window = MainWindow()
        self.window.show()

        # self.window.setPalette(palette)

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
    # turn on high dpi scaling - must be done before creating app
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    
    QCoreApplication.setOrganizationName("LDG Electronics")
    QCoreApplication.setApplicationName("Device Manager")

    # Create the Qt Application
    app = MyApplication()

    # grab the keyboard interrupt signal 
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Run the main Qt loop
    result = app.exec_()

    SettingsManager().save_now()
    
    sys.exit(result)

if __name__ == "__main__":
    run()