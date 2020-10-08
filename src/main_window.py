from qt import *
import qtawesome as qta
import logging
from style import qcolors

from device_manager import DeviceManager
from remote_devices import DeviceClient, DeviceServer, RemoteStatusWidget

from command_palette import CommandPalette, Command
from tuner import Tuner
from manual_tuner import ManualTuner
from servitor import ServitorWidget
from diagnostics import DiagnosticWidget
from device_controls import DeviceControlsDockWidget
from log_monitor import LogMonitorDockWidget
from sensor_calibration import CalibrationWidget

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
        self.remote_widget = RemoteStatusWidget(self, client=self.client, server=self.server)

        self.manual_tuner = ManualTuner()
        self.device_controls = DeviceControlsDockWidget(self)
        self.servitor = ServitorWidget()
        self.diagnostics = DiagnosticWidget()
        self.calibration = CalibrationWidget()

        self.addActions([
            Command("Preferences: Open Settings (JSON)", self),
            Command("Preferences: Open Settings (UI)", self, shortcut='Ctrl+,'),
            Command("Device Manager: Check for port changes", self),
            Command("Quit Application", self, triggered=self.close),
        ])

        # must be after Command objects are created by various modules
        self.command_palette = CommandPalette(self)

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.setContentsMargins(QMargins(3, 3, 3, 0))

        self.tabs.addTab(self.servitor, 'Servitor')
        self.tabs.addTab(self.diagnostics, 'Diagnostics')
        self.tabs.addTab(self.manual_tuner, 'Manual Tuner')
        self.tabs.addTab(self.calibration, 'Calibration')

        i = self.qsettings.value('selected_tab', 0)
        if i > self.tabs.count():
            i = self.tabs.count()
        self.tabs.setCurrentIndex(i)
        self.tabs.currentChanged.connect(lambda i: self.qsettings.setValue('selected_tab', i))

        # init dockwidget settings
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setDockNestingEnabled(True)

        self.init_toolbar()
        self.init_statusbar()

        self.load_settings() # do this last

        # def print_all_children(obj, prefix=''):
        #     for child in obj.children():
        #         print(prefix, child)
        #         print_all_children(child, '  ' + prefix )

        # print_all_children(self)
    
    def init_toolbar(self):
        self.tool = QToolBar()
        self.tool.setObjectName('toolbar')
        self.tool.setMovable(False)
        self.tool.setIconSize(QSize(40, 40))

        self.tool.addAction(QAction(qta.icon('ei.adjust-alt', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.check-empty', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.lines', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.random', color='gray'), '', self.tool))

        empty = QWidget(self.tool)
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
        self.tool.addWidget(empty)

        self.addToolBar(Qt.LeftToolBarArea, self.tool)

    def init_statusbar(self):
        self.status = QToolBar()
        self.status.setObjectName('statusbar')
        self.status.setMovable(False)
        self.status.setIconSize(QSize(30, 30))
        self.addToolBar(Qt.BottomToolBarArea, self.status)

        # settings button
        settings_btn = QToolButton(self.status, icon=qta.icon('fa.gear', color='gray'))
        menu = QMenu(settings_btn)
        settings_btn.setMenu(menu)
        settings_btn.setPopupMode(QToolButton.InstantPopup)
        self.status.addWidget(settings_btn)
        
        # settings popup menu
        menu.addAction(self.command_palette.action)
        menu.addSeparator()
        menu.addAction(self.device_controls.toggleViewAction())
        menu.addAction(self.log_monitor.toggleViewAction())

        menu.addSeparator()
            
        menu.addAction(QAction('&Exit', menu, 
            shortcut='Ctrl+Q', 
            statusTip='Exit application',
            triggered=self.close))
        
        # spacer widget
        self.status.addWidget(QWidget(sizePolicy=QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)))
        
        self.status.addWidget(self.remote_widget)

    def closeEvent(self, event):
        self.dm.scan_timer.stop()
        self.dm.update_timer.stop()
        self.dm.close()
        self.servitor.radio.timeout.timer.stop()
        self.calibration.worker.stop()
        self.calibration.thread.terminate()
        
        self.save_settings()

        super().closeEvent(event)

    def save_settings(self):
        self.qsettings.setValue("window_geometry", self.saveGeometry())
        self.qsettings.setValue("window_state", self.saveState())

    def load_settings(self):
        if self.qsettings.value("window_geometry") is not None:
            self.restoreGeometry(self.qsettings.value("window_geometry"))
        if self.qsettings.value("windowState") is not None:
            self.restoreState(self.qsettings.value("windowState"))