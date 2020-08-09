import logging
from device_client import DeviceClient
from qt import *
from device_manager import DeviceManager
from device_server import DeviceServer
from device_client import DeviceClient
from device_controls import DeviceControls
from servitor import Servitor
from tuner import Tuner
from settings import Settings, SettingsManager
from thread import WorkerControls
from command_palette import CommandPalette

from log_monitor import LogMonitor
import logging
import qtawesome as qta


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LDG Device Manager")

        self.qsettings = QSettings( 'LDG Electronics', 'BenchManager')
        
        self.setDockNestingEnabled(True)
        self.setAnimated(True)

        self.log_monitor = LogMonitor()

        self.command_palette = CommandPalette(self)
        self.dm = DeviceManager()
        self.server = DeviceServer()
        self.client = DeviceClient()
        self.tuner = Tuner()
        self.tuner_controls = self.tuner.controls
        self.worker_controls = WorkerControls()
        self.device_controls = DeviceControls(self.client)
        self.servitor = Servitor()

        self.dm.connect_to([
            self.server,
            self.client,
            self.tuner,
            self.device_controls,
            self.tuner_controls,
            self.servitor,
        ])
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

        self.addDockWidget(self.device_controls.starting_area, self.device_controls)
        self.addDockWidget(self.tuner_controls.starting_area, self.tuner_controls)
        self.addDockWidget(self.worker_controls.starting_area, self.worker_controls)
        self.addDockWidget(self.log_monitor.starting_area, self.log_monitor)

        # self.device_controls.hide()
        self.tuner_controls.hide()
        self.worker_controls.hide()
        self.log_monitor.hide()

        self.area = QMdiArea()
        self.area.addSubWindow(self.servitor)
        self.servitor.setWindowState(Qt.WindowMaximized)
        self.setCentralWidget(self.area)
        self.init_menu_bar()

        self.statusBar().addPermanentWidget(self.client.status_widget)
        self.statusBar().setFixedHeight(25)
        self.statusBar().setContentsMargins(0, 0, 0, 2)

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

        # do this last
        if self.qsettings.value("window_geometry") is not None:
            self.restoreGeometry(self.qsettings.value("window_geometry"))
        if self.qsettings.value("windowState") is not None:
            self.restoreState(self.qsettings.value("windowState"))

    def moveEvent(self, event):
        self.command_palette.center()

    def closeEvent(self, event):
        self.dm.scan_timer.stop()
        self.dm.update_timer.stop()
        self.servitor.control_panel.radio.timeout_timer.stop()
        
        self.qsettings.setValue("window_geometry", self.saveGeometry())
        self.qsettings.setValue("window_state", self.saveState())

        super().closeEvent(event)

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