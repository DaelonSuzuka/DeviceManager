from device_client import DeviceClient
from qt import *
import qtawesome as qta
import logging
from style import qcolors

from device_manager import DeviceManager
from device_server import DeviceServer
from device_client import DeviceClient
from settings import SettingsManager

from command_palette import CommandPalette, Command
from tuner import Tuner
from manual_tuner import ManualTuner
from servitor import ServitorWidget
from diagnostics import DiagnosticWidget
from device_controls import DeviceControlsDockWidget
from log_monitor import LogMonitorDockWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle("LDG Device Manager")
        self.qsettings = QSettings()

        # init first so it can install on the root logger
        self.log_monitor = LogMonitorDockWidget(self)

        self.dm = DeviceManager(self)
        self.server = DeviceServer(self)
        self.client = DeviceClient(self)
        self.manual_tuner = ManualTuner()
        self.device_controls = DeviceControlsDockWidget(self)
        self.servitor = ServitorWidget()
        self.diagnostics = DiagnosticWidget()

        self.addActions([
            Command("Preferences: Open Settings (JSON)", self),
            Command("Preferences: Open Settings (UI)", self, shortcut='Ctrl+,'),
            Command("Device Manager: Check for port changes", self),
            Command("Device Manager: Fizz", self),
            Command("Device Manager: Buzz", self),
            Command("Quit Application", self, triggered=self.close),
        ])

        # must be after Command objects are created by various modules
        self.command_palette = CommandPalette(self)

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.setContentsMargins(QMargins(3, 3, 3, 0))

        self.tabs.addTab(self.manual_tuner, 'Manual Tuner')

        # init dockwidget settings
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setDockNestingEnabled(True)

        # self.init_menu_bar()
        self.init_toolbar()

        self.load_settings() # do this last

        # def print_all_children(obj, prefix=''):
        #     for child in obj.children():
        #         print(prefix, child)
        #         print_all_children(child, '  ' + prefix )

        # print_all_children(self)
    
    def init_menu_bar(self):
        menu = QMenuBar()
        file_ = menu.addMenu('File')

        file_.addAction(QAction('&Settings', self, 
            shortcut='Ctrl+,', 
            statusTip='Open settings',
            triggered=lambda: SettingsManager().show_dialog()))

        file_.addSeparator()

        file_.addAction(QAction('&Exit', self, 
            shortcut='Ctrl+Q', 
            statusTip='Exit application',
            triggered=self.close))
    
        view = menu.addMenu('View')
    
        view.addAction(self.command_palette.action)
        view.addSeparator()
        view.addAction(self.device_controls.toggleViewAction())
        view.addAction(self.log_monitor.toggleViewAction())

        settings = menu.addMenu('Settings')
        settings.addAction(QAction('Settings', menu))

        plugins = menu.addMenu('Plugins')
        plugins.addAction(QAction('Plugins', menu))

        help_ = menu.addMenu('Help')
        help_.addAction(QAction('Help', menu))

        self.setMenuBar(menu)

    def init_toolbar(self):
        self.tool = QToolBar()
        self.tool.setObjectName('toolbar')
        self.tool.setMovable(False)
        self.tool.setIconSize(QSize(30, 30))
        self.addToolBar(Qt.BottomToolBarArea, self.tool)

        # settings button
        settings_btn = QToolButton(self.tool, icon=qta.icon('mdi.settings', color='gray'))
        menu = QMenu(settings_btn)
        settings_btn.setMenu(menu)
        settings_btn.setPopupMode(QToolButton.InstantPopup)
        self.tool.addWidget(settings_btn)
        
        # settings popup menu
        menu.addAction(self.command_palette.action)
        menu.addSeparator()
        menu.addAction(self.device_controls.toggleViewAction())
        menu.addAction(self.log_monitor.toggleViewAction())

        menu.addSeparator()
        menu.addAction(QAction('&Settings', menu, 
            shortcut='Ctrl+,', 
            statusTip='Open settings',
            triggered=lambda: SettingsManager().show_dialog()))
            
        menu.addAction(QAction('&Exit', menu, 
            shortcut='Ctrl+Q', 
            statusTip='Exit application',
            triggered=self.close))
        
        # spacer widget
        self.tool.addWidget(QWidget(sizePolicy=QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)))
        
        self.tool.addWidget(self.client.status_widget)

    def closeEvent(self, event):
        self.dm.scan_timer.stop()
        self.dm.update_timer.stop()
        self.dm.close()
        self.servitor.radio.timeout.timer.stop()
        
        self.save_settings()
        SettingsManager().save_now()

        super().closeEvent(event)

    def save_settings(self):
        self.qsettings.setValue("window_geometry", self.saveGeometry())
        self.qsettings.setValue("window_state", self.saveState())

    def load_settings(self):
        if self.qsettings.value("window_geometry") is not None:
            self.restoreGeometry(self.qsettings.value("window_geometry"))
        if self.qsettings.value("windowState") is not None:
            self.restoreState(self.qsettings.value("windowState"))