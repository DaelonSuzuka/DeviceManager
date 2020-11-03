from qt import *
import qtawesome as qta

from device_manager import DeviceManager
from remote_devices import DeviceClient, DeviceServer, RemoteStatusWidget

from command_palette import CommandPalette, Command
from device_controls import DeviceControlsDockWidget
from log_monitor import LogMonitorDockWidget

from plugins.apps import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle("LDG Device Manager")

        self.load_settings()

        # init first so it can install on the root logger
        self.log_monitor = LogMonitorDockWidget(self)

        self.dm = DeviceManager(self)
        self.server = DeviceServer(self)
        self.client = DeviceClient(self)
        self.remote_widget = RemoteStatusWidget(self, client=self.client, server=self.server)
        self.device_controls = DeviceControlsDockWidget(self)

        self.setContentsMargins(QMargins(3, 3, 3, 0))

        self.apps = [app(self) for app in apps]

        self.tabs = PersistentTabWidget('main_window_tabs', tabs=self.apps)
        self.setCentralWidget(self.tabs)

        self.tab_shortcuts = []
        for i in range(10):
            shortcut = QShortcut(f'Ctrl+{i + 1}', self, activated=lambda i=i: self.tabs.setCurrentIndex(i))
            self.tab_shortcuts.append(shortcut)

        self.commands = [
            Command("Preferences: Open Settings (JSON)"),
            Command("Preferences: Open Settings (UI)", shortcut='Ctrl+,'),
            Command("Device Manager: Check for port changes"),
            Command("Quit Application", triggered=self.close),
        ]

        # must be after Command objects are created by various modules
        self.command_palette = CommandPalette(self)

        # init dockwidget settings
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setDockNestingEnabled(True)

        # self.init_toolbar()
        self.init_statusbar()
    
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
        self.dm.close()

        for app in self.apps:
            app.close()
        
        self.save_settings()

        super().closeEvent(event)

    def save_settings(self):
        QSettings().setValue("window_geometry", self.saveGeometry())
        QSettings().setValue("window_state", self.saveState())

    def load_settings(self):
        if QSettings().value("window_geometry") is not None:
            self.restoreGeometry(QSettings().value("window_geometry"))
        if QSettings().value("window_state") is not None:
            self.restoreState(QSettings().value("window_state"))