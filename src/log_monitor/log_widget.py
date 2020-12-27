from qt import *
from .log_table_view import LogTableView
from .log_filter_controls import FilterControls
from .log_database_handler import DatabaseHandler
from command_palette import CommandPalette, Command


class LogMonitorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_name = "Log Monitor"

        self.commands = [
            Command("Log Monitor: Switch profile", triggered=self.open_profile_prompt),
        ]

        self.log_table = LogTableView()
        DatabaseHandler.register_callback(self.log_table.schedule_refresh)

        self.filter_controls = FilterControls()
        self.filter_controls.filter_updated.connect(self.log_table.set_filter)
        self.filter_controls.update_filter()

        # temporary
        db = QSqlDatabase.database()
        query = db.exec_("SELECT Source FROM 'log'")
        loggers = set()
        while query.next():
            loggers.add(query.value(0))
        self.filter_controls.logger_filter.register_loggers(loggers)
        
        hbox = QHBoxLayout(self)

        splitter = QSplitter(self)
        hbox.addWidget(splitter)
        # splitter.setContentsMargins(10, 10, 10, 10)
        splitter.addWidget(self.filter_controls)
        splitter.addWidget(self.log_table)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 10)

    def open_profile_prompt(self):
        profiles = list(self.filter_controls.settings['profiles'].keys())

        self.completer = QCompleter(self, profiles)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)

        QTimer.singleShot(0, lambda: CommandPalette().open(
            placeholder='Select a profile',
            cb=lambda result: print(result),
            completer=self.completer
        ))
            

class LogMonitorDockWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__('Log Monitor', parent=parent)
        self.setObjectName('LogMonitor')

        self.setWidget(LogMonitorWidget(self))

        self.commands = [
            Command("Log Monitor: Show log monitor", triggered=self.show, shortcut='Ctrl+L'),
            Command("Log Monitor: Hide log monitor", triggered=self.hide),
        ]

        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dockLocationChanged.connect(lambda: QTimer.singleShot(0, self.adjust_size))

        self.starting_area = Qt.BottomDockWidgetArea

        if not self.parent().restoreDockWidget(self):
            self.parent().addDockWidget(self.starting_area, self)
        
        self.closeEvent = lambda x: self.hide()

    def adjust_size(self):
        if self.isFloating():
            self.adjustSize()
            
    def toggleViewAction(self):
        action = super().toggleViewAction()
        action.setShortcut('Ctrl+L')
        return action