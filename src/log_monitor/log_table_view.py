from qt import *
import time


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

        where = []
        if self.filter['current_session_only']:
            where.append(f"TimeStamp > '{session_start_time}'")

        if self.filter['text']:
            where.append(f"Message LIKE '%{self.filter['text']}%'")
        
        if self.filter['visible_loggers']:
            sources = []

            for logger in self.filter['visible_loggers']:
                levels = ', '.join([f'"{l}"' for l in self.filter["loggers"][logger]])
                s = f'(Source = "{logger}" AND LogLevelName IN ({levels}))'
                sources.append(s)
            
            where.append(f"({' OR '.join(sources)})")

        if where:
            query += f' WHERE ' + ' AND '.join(where)
        
        query += f" LIMIT {self.query_limit}"
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

