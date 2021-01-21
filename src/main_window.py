from qt import *
import qtawesome as qta

from networking import NetworkStatusWidget
from command_palette import CommandPalette, Command
from device_controls import DeviceControlsDockWidget
from log_monitor import LogMonitorWidget, LogMonitorDropdown

from plugins.apps import *


class MainWindow(BaseMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("LDG Device Manager")

        self.log_monitor = LogMonitorDropdown(self)        
        self.network_status = NetworkStatusWidget(self)
        self.device_controls = DeviceControlsDockWidget(self)

        self.setContentsMargins(QMargins(3, 3, 3, 0))

        self.apps = [app(self) for app in apps]
        # self.apps.append(self.log_monitor)

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
        self.tool = BaseToolbar(self, 'toolbar', location='left', size=40)

        self.tool.addAction(QAction(qta.icon('ei.adjust-alt', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.check-empty', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.lines', color='gray'), '', self.tool))
        self.tool.addAction(QAction(qta.icon('ei.random', color='gray'), '', self.tool))

        self.tool.add_spacer()

    def init_statusbar(self):
        self.status = BaseToolbar(self, 'statusbar', location='bottom', size=30)

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
        
        self.status.add_spacer()

        self.status.addWidget(self.network_status)

    def closeEvent(self, event):
        for app in self.apps:
            app.close()

        super().closeEvent(event)