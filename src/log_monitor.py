import logging
from qt import *
from collections import deque
import json
import time
import qtawesome as qta
from style import colors
from command_palette import CommandPalette, Command


INVALID_INDEX = QModelIndex()
log_levels = {
    'DEBUG': colors.aqua,
    'INFO': colors.green,
    'WARNING': colors.yellow,
    'ERROR': colors.orange,
    'CRITICAL': colors.red,
}
level_map = {
    'D': 'DEBUG',
    'I': 'INFO',
    'W': 'WARNING',
    'E': 'ERROR',
    'C': 'CRITICAL',
}


initial_sql = """CREATE TABLE IF NOT EXISTS log(
                    TimeStamp TEXT,
                    Source TEXT,
                    LogLevel INT,
                    LogLevelName TEXT,
                    Message TEXT,
                    Args TEXT,
                    Module TEXT,
                    FuncName TEXT,
                    LineNo INT,
                    Exception TEXT,
                    Process INT,
                    Thread TEXT,
                    ThreadName TEXT
               )"""

insertion_sql = """INSERT INTO log(
                    TimeStamp,
                    Source,
                    LogLevel,
                    LogLevelName,
                    Message,
                    Args,
                    Module,
                    FuncName,
                    LineNo,
                    Exception,
                    Process,
                    Thread,
                    ThreadName
               )
               VALUES (
                    '%(dbtime)s',
                    '%(name)s',
                    %(levelno)d,
                    '%(levelname)s',
                    '%(msg)s',
                    '%(args)s',
                    '%(module)s',
                    '%(funcName)s',
                    %(lineno)d,
                    '%(exc_text)s',
                    %(process)d,
                    '%(thread)s',
                    '%(threadName)s'
               );
               """


class LogMonitorHandler(logging.Handler):
    """A logging.Handler subclass that redirects log records to the LogMonitor
    """
    def __init__(self):
        super().__init__()
        self.record_added = None
        self.formatter = logging.Formatter("%(asctime)s")
        
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('log.db')
        db.open()
        db.exec_(initial_sql)

    def format_time(self, record):
        record.dbtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))

    def emit(self, record):
        self.format(record)
        self.format_time(record)
        
        if record.exc_info:  # for exceptions
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
        else:
            record.exc_text = ""

        # Insert the log record
        sql = insertion_sql % record.__dict__
        
        db = QSqlDatabase.database()
        db.exec_(sql)

        if self.record_added != None:
            self.record_added()

    def write(self, m):
        pass


log_handler = LogMonitorHandler()


class LoggerDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        value = index.data(Qt.DisplayRole)
        checked = index.data(Qt.UserRole)

        if value is None:
            return

        painter.save()

        if len(value) == 1:
            if option.state & QStyle.State_Selected and checked:
                painter.setPen(QPen(log_levels[level_map[value]]))
            else: 
                painter.setPen(QPen('gray'))
            painter.drawText(option.rect, Qt.AlignCenter, value)
        else:
            if option.state & QStyle.State_Selected:
                painter.setPen(QPen('lightgray'))
            else: 
                painter.setPen(QPen('gray'))
            painter.drawText(option.rect, Qt.AlignLeft, value)

        painter.restore()


class LoggerTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent, name, full_name):
        super().__init__(parent)

        self.setText(0, name)
        self.name = name
        self.full_name = full_name

        self.levels = {
            'DEBUG': True,
            'INFO': True,
            'WARNING': True,
            'ERROR': True,
            'CRITICAL': True,
        }

        self.update_data()
        self.selected = False

    def clicked(self, column):
        if column == 0:
            if self.full_name != 'global':
                self.setSelected(not self.isSelected())
            else:
                self.selected = not self.selected
        else:
            if self.data(column, Qt.UserRole):
                self.setData(column, Qt.UserRole, False)
                self.levels[level_map[self.text(column)]] = False
            else:
                self.setData(column, Qt.UserRole, True)
                self.levels[level_map[self.text(column)]] = True

    def double_clicked(self, column):        
        def select_children(item, state):
            item.setSelected(state)
            for i in range(item.childCount()):
                select_children(item.child(i), state)

        if column == 0:
            if self.full_name != 'global':
                state = self.isSelected()
            else:
                state = self.selected
            
            for i in range(self.childCount()):
                select_children(self.child(i), state)

    def update_data(self):
        for i, level in enumerate(self.levels):
            self.setData(i + 1, Qt.UserRole, self.levels[level])
            self.setText(i + 1, level[:1])
            self.setTextAlignment(i + 1, Qt.AlignCenter)

    def set_levels(self, level_filter=[]):
        for level in level_filter:
            if level in self.levels:
                self.levels[level] = True

        self.update_data()

    def get_levels(self):
        return [level for level in self.levels if self.levels[level]]

    def set_all_levels(self, state: bool):
        for level in self.levels:
            self.levels[level] = state
        self.update_data()


class LoggerTreeWidget(QTreeWidget):
    filter_updated = Signal()

    def __init__(self):
        super().__init__()
        
        self.setItemDelegate(LoggerDelegate())
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setRootIsDecorated(False)
        self.setIndentation(10)
        self.setStyleSheet("QTreeView::branch { border-image: url(none.png); }" );
        self.setUniformRowHeights(True)
        self.setExpandsOnDoubleClick(False)
        self.setItemsExpandable(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.header().setMinimumSectionSize(1)
        self.header().hide()

        self.setColumnCount(7)
        self.setColumnWidth(1,15)
        self.setColumnWidth(2,15)
        self.setColumnWidth(3,15)
        self.setColumnWidth(4,15)
        self.setColumnWidth(5,15)

        self.loggers = {}
        self.visible_loggers = []

        self.itemClicked.connect(self.click)
        self.itemDoubleClicked.connect(self.double_click)
        self.itemSelectionChanged.connect(self.selection_changed)

        self.root = LoggerTreeWidgetItem(self, 'global', 'global')
        self.loggers['global'] = self.root
        self.root.setSelected(True)

    def click(self, item, column):
        item.clicked(column)
        self.selection_changed()

    def double_click(self, item, column):
        item.double_clicked(column)
        self.selection_changed()

    def selection_changed(self):
        self.visible_loggers = [item.full_name for item in self.selectedItems()]
        self.filter_updated.emit()

    def register_logger(self, full_name):
        if full_name in self.loggers:
            return 
        else:
            parts = full_name.rsplit('.', 1)  # split off the last name only
            name = parts[-1]

            if len(parts) == 1:
                parent = self.root
            else:
                if parts[0] not in self.loggers:
                    self.register_logger(parts[0])
                parent = self.loggers[parts[0]]

            self.loggers[full_name] = LoggerTreeWidgetItem(parent, name, full_name)
            self.loggers[full_name].setSelected(True)

        self.expandAll()
        self.selection_changed()

    def register_loggers(self, loggers):
        for name in loggers:
            self.register_logger(name)

    def set_visible_loggers(self, logger_filter):
        for logger in logger_filter:
            self.setItemSelected(self.loggers[logger], True)

    def contextMenuEvent(self, event):
        menu = QMenu()
        pos = event.globalPos()
        menu.addAction(QAction('Select Only', menu, triggered=lambda: self.select_only(pos)))
        menu.addAction(QAction('Select All', menu, triggered=self.select_all))
        menu.addAction(QAction('Deselect All', menu, triggered=self.deselect_all))
        menu.addAction(QAction('All Levels', menu, triggered=lambda: self.enable_all_levels(pos)))
        menu.addAction(QAction('No Levels', menu, triggered=lambda: self.disable_all_levels(pos)))
        menu.addAction(QAction('Enable Everything', menu, triggered=self.enable_everything))
        menu.addAction(QAction('Disable Everything', menu, triggered=self.disable_everything))
        menu.exec_(event.globalPos())

    def set_levels_of_children(self, item, state):
        if hasattr(item, 'set_all_levels'):
            item.set_all_levels(state)
        for i in range(item.childCount()):
            self.set_levels_of_children(item.child(i), state)

    def enable_everything(self):
        self.select_all()
        self.set_levels_of_children(self.invisibleRootItem(), True)

    def disable_everything(self):
        self.deselect_all()
        self.set_levels_of_children(self.invisibleRootItem(), False)

    def enable_all_levels(self, pos):
        self.itemAt(self.viewport().mapFromGlobal(pos)).set_all_levels(True)
        self.selection_changed()

    def disable_all_levels(self, pos):
        self.itemAt(self.viewport().mapFromGlobal(pos)).set_all_levels(False)
        self.selection_changed()

    def set_visible_loggers(self, visible_loggers):
        def set_visible(item):
            if hasattr(item, 'full_name'):
                if item.full_name in visible_loggers:
                    item.setSelected(True)
                else:
                    item.setSelected(False)

            for i in range(item.childCount()):
                set_visible(item.child(i))

        set_visible(self.invisibleRootItem())

    def select_all(self):
        def select_children(item):
            item.setSelected(True)
            for i in range(item.childCount()):
                select_children(item.child(i))

        select_children(self.invisibleRootItem())

    def deselect_all(self):
        self.clearSelection()
        self.root.setSelected(True)

    def select_only(self, pos):
        self.deselect_all()
        self.itemAt(self.viewport().mapFromGlobal(pos)).setSelected(True)
        self.selection_changed()


class ProfileSelector(QWidget):
    added = Signal(str)
    removed = Signal(str)
    changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet('QPushButton { max-width: 20px; }')

        self.selector = QComboBox()
        self.editor = QLineEdit()

        self.add = QPushButton(qta.icon('fa.plus-square-o', color='lightgray'), '')
        self.accept = QPushButton(qta.icon('fa5.check-square', color='lightgray'), '')
        self.edit = QPushButton(qta.icon('fa.pencil-square-o', color='lightgray'), '')

        self.selector.currentIndexChanged.connect(self.on_change)
        self.add.clicked.connect(self.on_add)
        self.accept.clicked.connect(self.on_accept)
        self.editor.returnPressed.connect(self.on_accept)
        
        grid = CGridLayout(self, margins=(0, 0, 0, 0), spacing=2)

        grid.add(self.selector, 0, 0, 1, 3)
        grid.add(self.editor, 0, 0, 1, 3)
        grid.add(self.add, 0, 3)
        grid.add(self.accept, 0, 3)
        grid.add(self.edit, 0, 4)

        self.accept.hide()
        self.editor.hide()

    def on_change(self):
        name = self.selector.currentText()
        self.changed.emit(name)

    def on_add(self):
        self.accept.show()
        self.add.hide()
        self.selector.hide()
        self.editor.show()
        self.editor.setFocus()

    def on_accept(self):
        self.accept.hide()
        self.add.show()
        self.selector.show()
        self.editor.hide()

        name = self.editor.text()
        if len(name) > 0:
            self.added.emit(name)
        self.editor.clear()

    def on_remove(self):
        name = self.selector.currentText()
        self.removed.emit(name)


class FilterControls(QStackedWidget):
    filter_updated = Signal(dict)

    empty_profile = {
        'loggers': {
            'global': ['DEBUG','INFO','WARNING','ERROR','CRITICAL'],
        },
        'visible_loggers': [
            'global'
        ],
        'text': '',
        'current_session_only': True,
    }

    default_settings = {
        'selected_profile': 'default',
        'registered_loggers': ['global'],
        'profiles': {
            'default': empty_profile
        }
    }

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QTreeWidget {
                selection-background-color: transparent;
                selection-color: lightgray; 
                color: gray;
            }
        """)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # create widgets
        self.profiles = ProfileSelector()

        self.text_filter = QLineEdit()
        self.text_filter.textChanged.connect(self.update_filter)
        self.text_filter.setClearButtonEnabled(True)
        self.text_filter.setPlaceholderText('filter by text')

        self.logger_filter = LoggerTreeWidget()

        # load settings and send filter components to widgets
        self.settings = QSettings().value('log_monitor', self.default_settings)

        profiles = self.settings['profiles']
        current_profile_name = self.settings['selected_profile']
        if current_profile_name not in profiles:
            current_profile_name = list(profiles.keys())[0]
        self.current_profile = profiles[current_profile_name]

        self.logger_filter.register_loggers(self.settings['registered_loggers'])
        self.profiles.selector.addItems(profiles)

        for logger in self.current_profile['loggers']:
            self.logger_filter.register_logger(logger)

        self.logger_filter.set_visible_loggers(self.current_profile['visible_loggers'])

        # connect signals
        self.logger_filter.filter_updated.connect(self.update_filter)
        self.profiles.selector.setCurrentIndex(self.profiles.selector.findText(current_profile_name))
        self.profiles.changed.connect(self.change_profile)
        self.profiles.added.connect(self.add_profile)
        self.profiles.removed.connect(self.remove_profile)
        self.profiles.edit.clicked.connect(lambda: self.setCurrentIndex(1))

        # send the filter to the model
        self.update_filter()

        self.addWidget(QWidget())
        self.addWidget(QWidget())

        # controls layout
        grid = CGridLayout(self.widget(0), margins=(0, 0, 0, 0))
        grid.add(self.profiles, 0, 0, 1, 5)
        grid.add(self.text_filter, 1, 0, 1, 5)
        grid.add(self.logger_filter, 2, 0, 1, 5)

        # editor layout
        grid = CGridLayout(self.widget(1), margins=(0, 0, 0, 0))
        grid.add(QPushButton('X', maximumWidth=20, clicked=lambda: self.setCurrentIndex(0)), 0, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)

    def save_settings(self):
        QSettings().setValue('log_monitor', self.settings)

    def add_profile(self, name):
        new_profile = dict(self.empty_profile)
        self.settings['profiles'][name] = new_profile
        self.profiles.selector.addItem(name)
        self.profiles.selector.setCurrentIndex(self.profiles.selector.findText(name))

    def remove_profile(self, name):
        index = self.profiles.selector.findText(name)
        self.profiles.selector.removeItem(index)

        self.settings['profiles'].pop(name)
        self.save_settings()

    def change_profile(self, profile_name):
        self.settings['selected_profile'] = profile_name

        self.current_profile = self.settings['profiles'][profile_name]
        self.logger_filter.set_visible_loggers(self.current_profile['visible_loggers'])
        self.update_filter()
        self.save_settings()

    def update_filter(self):
        text = self.text_filter.text()
        loggers = {item.full_name: item.get_levels() for _, item in self.logger_filter.loggers.items()}
        visible_loggers = self.logger_filter.visible_loggers

        self.settings['registered_loggers'] = list(self.logger_filter.loggers.keys())
        self.current_profile['text'] = text
        self.current_profile['loggers'] = loggers
        self.current_profile['visible_loggers'] = visible_loggers

        self.filter_updated.emit(self.current_profile)
        self.save_settings()


class Column:
    def __init__(self, name=None, title=None, visible=True, width=50):
        self.name = name
        self.title = title
        self.visible = visible
        self.width = width

    def set_visibility(self, visible):
        self.visible = visible


class TableHeader(QObject):
    def __init__(self, header_view):
        super().__init__()
        self.header_view = header_view
        self.columns = [
            Column('asctime', 'Time', width=170),
            Column('levelname', 'Level', width=60),
            Column('name', 'Name', width=180),
            Column('port', 'Port', False, width=225),
            Column('guid', 'GUID', width=40),
            Column('profile_name', 'Device', False, width=60),
            Column('levelno', '#', False, width=22),
            Column('funcName', 'Function', False, width=80),
            Column('pathname', 'Path', False, width=120),
            Column('filename', 'File', False, width=75),
            Column('lineno', 'Line #', False, width=35),
            Column('module', 'Module', False, width=50),
            Column('process', 'Process', False, width=40),
            Column('processName', 'Process name', False, width=80),
            Column('thread', 'Thread', False, width=100),
            Column('threadName', 'Thread name', False, width=70),
            Column('message', 'Message', True, width=10),
        ]
        self.regen_visible()

    def eventFilter(self, object, event):
        """
        The problem with headerView.sectionResized is that it gets called way
        too much, often pointlessly or in annoying ways. So I decided that
        instead I'll listen for mouse releases on the headerView and save the
        whole header whenever that event comes through the filter.

        Is this the best solution or the worst solution?
        I guess we'll never know.
        """
        if event.type() == QEvent.MouseButtonRelease:
            self.mouse_released()
            return True
        return False

    def mouse_released(self):
        for section in range(self.header_view.count()):
            col = self.visible_columns[section]
            col.width = self.header_view.sectionSize(section)

    def replace_columns(self, new_columns):
        self.columns = new_columns
        self.regen_visible()

    def regen_visible(self):
        self.visible_columns = [c for c in self.columns if c.visible]
        self.visible_names = set([c.name for c in self.visible_columns])
        for i, column in enumerate(self.visible_columns):
            self.header_view.resizeSection(i, column.width)
    
    def __getitem__(self, index):
        return self.visible_columns[index]

    @property
    def column_count(self):
        return len(self.visible_columns)


session_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class Profile:    
    def __init__(self):
        self.columns = [
            Column("TimeStamp", "Time", width=170, visible=True),
            Column("Source", "Source", width=100, visible=True),
            Column("LogLevel", "Level", width=100, visible=False),
            Column("LogLevelName", "LevelName", width=80, visible=True),
            Column("Message", "Message", width=100, visible=True),
            Column("Args", "Args", width=100, visible=False),
            Column("Module", "Module", width=100, visible=False),
            Column("FuncName", "Func", width=100, visible=False),
            Column("LineNo", "Line", width=100, visible=False),
            Column("Exception", "Exception", width=100, visible=False),
            Column("Process", "Process", width=100, visible=False),
            Column("Thread", "Thread", width=100, visible=False),
            Column("ThreadName" "ThreadName",width=100, visible=False),
        ]
        self.filter = {}
        self.query_limit = 1000

    def get_query_string(self):
        query = "SELECT "
        query += ', '.join([f'"{col.name}"' for col in self.columns if col.visible])
        query += " FROM 'log'"
        
        # print(self.filter)

        where = []
        if self.filter['current_session_only']:
            where.append(f"TimeStamp > '{session_start_time}'")

        if self.filter['text']:
            where.append(f"Message LIKE '%{self.filter['text']}%'")
        
        if self.filter['visible_loggers']:
            sources = [f'"{s}"' for s in self.filter['visible_loggers']]
            where.append(f"Source IN ({', '.join(sources)})")

        if where:
            query += f' WHERE ' + ' AND '.join(where)
        
        query += f" LIMIT {self.query_limit}"
        # print(query)
        return query


class LogTableView(QTableView):
    def __init__(self):
        super().__init__()
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(12)

        header = self.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.header_menu)

        self.profile = Profile()

        self.db_model = QSqlQueryModel(self)

        self.setModel(self.db_model)
        self.need_to_refresh = False
        
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.attempt_refresh)
        self.scan_timer.start(250)
    
    def attempt_refresh(self):
        if self.need_to_refresh:
            self.refresh()
            self.need_to_refresh = False

    def refresh(self):
        self.db_model.setQuery(self.profile.get_query_string())
        while self.db_model.canFetchMore():
            self.db_model.fetchMore()

        self.scrollToBottom()

    def header_menu(self):
        menu = QMenu()

        for column in self.profile.columns:
            action = QAction(column.title, menu, checkable=True)
            action.setChecked(column.visible)
            action.triggered.connect(column.set_visibility)
            menu.addAction(action)

        menu.exec_(QCursor.pos())

        # self.table_header.regen_visible()
        # self.record_model.modelReset.emit()
        # self.set_columns_sizes()
        self.refresh()

    def db_changed(self):
        self.need_to_refresh = True

    def set_filter(self, filter):
        self.profile.filter = filter
        self.refresh()


class LogMonitorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_name = "Log Monitor"

        self.commands = [
            Command("Log Monitor: Switch profile", triggered=self.open_profile_prompt),
        ]

        self.log_table = LogTableView()
        log_handler.record_added = self.log_table.db_changed

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