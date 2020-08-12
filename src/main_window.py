from device_client import DeviceClient
from qt import *
from device_manager import DeviceManager
from device_server import DeviceServer
from device_client import DeviceClient
from device_controls import DeviceControls
from servitor import Servitor
from tuner import Tuner
from settings import SettingsManager
from command_palette import CommandPalette, Command

from log_monitor import LogMonitor
import logging
import qtawesome as qta


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle("LDG Device Manager")
        self.qsettings = QSettings()
        self.setAnimated(True)

        # init first so it can install on the root logger
        self.log_monitor = LogMonitor()

        self.command_palette = CommandPalette(self)

        self.dm = DeviceManager(self)
        self.server = DeviceServer()
        self.client = DeviceClient()
        self.tuner = Tuner()
        self.tuner_controls = self.tuner.controls
        self.device_controls = DeviceControls()
        self.servitor = Servitor()

        self.area = QMdiArea()
        self.area.addSubWindow(self.servitor)
        self.servitor.setWindowState(Qt.WindowMaximized)
        self.setCentralWidget(self.area)

        self.init_dock_widgets()
        self.init_menu_bar()
        self.init_statusbar()
        self.init_toolbar()

        self.load_settings() # do this last

        self.commands = [
            Command("Preferences: Open Settings (JSON)", self),
            Command("Preferences: Open Settings (UI)", self, shortcut='Ctrl+,'),
            Command("Device Manager: Check for port changes", self),
            Command("Device Manager: Fizz", self),
            Command("Device Manager: Buzz", self),
            Command("Close Window", self, triggered=self.close),
        ]

        # def print_all_children(obj, prefix=''):
        #     for child in obj.children():
        #         print(prefix, child)
        #         print_all_children(child, '  ' + prefix )

        # print_all_children(self)

    def closeEvent(self, event):
        self.dm.scan_timer.stop()
        self.dm.update_timer.stop()
        self.servitor.control_panel.radio.timeout_timer.stop()
        self.tuner.worker.slots.stop()
        self.tuner.thread.quit()
        
        self.save_settings()

        super().closeEvent(event)

    def init_dock_widgets(self):
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setDockNestingEnabled(True)

        self.addDockWidget(self.device_controls.starting_area, self.device_controls)
        self.addDockWidget(self.tuner_controls.starting_area, self.tuner_controls)
        self.addDockWidget(self.log_monitor.starting_area, self.log_monitor)

        # self.device_controls.hide()
        self.tuner_controls.hide()
        self.log_monitor.hide()
    
    def init_menu_bar(self):
        mb = MenuBar()
        mb.file_exit.triggered.connect(self.close)
        mb.file_settings.triggered.connect(lambda: SettingsManager().show_dialog())
        mb.view.addAction(self.command_palette.action)
        mb.view.addSeparator()
        mb.view.addAction(self.device_controls.toggleViewAction())
        mb.view.addAction(self.tuner_controls.toggleViewAction())
        mb.view.addAction(self.log_monitor.toggleViewAction())
        self.setMenuBar(mb)

    def init_statusbar(self):

        self.statusBar().setFixedHeight(25)
        self.statusBar().setContentsMargins(10, 0, 10, 3)
        self.statusBar().addPermanentWidget(self.client.status_widget)

    def init_toolbar(self):
        self.tool = QToolBar()
        self.tool.setObjectName('toolbar')
        self.tool.setMovable(False)
        self.tool.setIconSize(QSize(40, 40))

        self.tool.addAction(QAction(qta.icon('ei.adjust-alt', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.check-empty', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.lines', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.random', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.cogs', color='gray'), '', self.tool))

        self.addToolBar(Qt.LeftToolBarArea, self.tool)

    def save_settings(self):
        self.qsettings.setValue("window_geometry", self.saveGeometry())
        self.qsettings.setValue("window_state", self.saveState())

    def load_settings(self):
        if self.qsettings.value("window_geometry") is not None:
            self.restoreGeometry(self.qsettings.value("window_geometry"))
        if self.qsettings.value("windowState") is not None:
            self.restoreState(self.qsettings.value("windowState"))


class MenuBar(QMenuBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_menu()
        self.view_menu()

    def file_menu(self):        
        self.file = self.addMenu("&File")

        self.file_settings = QAction("&Settings", self)
        self.file_settings.setShortcut("Ctrl+,")
        self.file_settings.setStatusTip("Open settings")

        self.file_exit = QAction(QIcon("exit.png"), "&Exit", self)
        self.file_exit.setShortcut("Ctrl+Q")
        self.file_exit.setStatusTip("Exit application")

        self.file.addAction(self.file_settings)
        self.file.addSeparator()
        self.file.addAction(self.file_exit)
    
    def view_menu(self):        
        self.view = self.addMenu("&View")