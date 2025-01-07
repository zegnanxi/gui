from PySide6.QtWidgets import (
    QHeaderView, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QToolButton, QSplitter, QTableView, QStyledItemDelegate, QAbstractItemView)
from PySide6.QtGui import QFontMetrics, QIcon, QStandardItemModel
from PySide6.QtCore import Qt, QSize, Slot

from .progress_indicator import QProgressIndicator


class BaseFrame(QWidget):
    @staticmethod
    def _process_fields(fields, side):
        results = []
        for item in fields:
            if '.hs' in item:
                if side == 'Host Side':
                    results.append(item.replace('.hs', ''))
            elif '.ls' in item:
                if side == 'Line Side':
                    results.append(item.replace('.ls', ''))
            else:
                results.append(item)
        return results

    def __init__(self):
        super().__init__()
        self.mainLayout = QVBoxLayout()
        self.fetcher_thread = None

        # 添加spinner
        self.spinner = QProgressIndicator(self)
        self.spinner.hide()

        self.consoleWidget = ConsoleWidget()
        self.tableWidget = BaseTable(self.COLUMNS)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.tableWidget)
        self.splitter.addWidget(self.consoleWidget)
        self.splitter.setSizes([200, 100])

        self.mainLayout.addWidget(self.splitter)
        self.setLayout(self.mainLayout)

    def load_data(self):
        """基类的数据加载方法"""
        # 如果已有正在运行的线程，先停止它
        if self.fetcher_thread and self.fetcher_thread.isRunning():
            self.fetcher_thread.quit()
            self.fetcher_thread.wait()

        # self.tableWidget.setRowCount(0)
        self._show_loading_state()

        # 创建并启动新的数据获取线程
        self.fetcher_thread = self._create_dev_op_thread()
        if self.fetcher_thread:
            self.fetcher_thread.row_ready.connect(
                self.tableWidget.update_row)
            self.fetcher_thread.log_message.connect(
                self.consoleWidget.console.appendPlainText)
            self.fetcher_thread.finished.connect(
                self._hide_loading_state)
            self.fetcher_thread.start()

    def _show_loading_state(self):
        """显示加载状态"""
        # 获取主窗口
        main_window = self.window()

        # 显示spinner
        self.spinner.setParent(main_window)  # 将spinner的父窗口设置为主窗口
        self.spinner.show()

        # 计算相对于主窗口的中心位置
        center_x = main_window.width() // 2 - self.spinner.width() // 2
        center_y = main_window.height() // 2 - self.spinner.height() // 2
        self.spinner.move(center_x, center_y)

        # 启动spinner动画
        self.spinner.start()
        self.setEnabled(False)

    def _hide_loading_state(self):
        """隐藏加载状态"""
        self.spinner.stop()
        self.spinner.hide()
        self.setEnabled(True)

    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        if self.spinner and not self.spinner.isHidden():
            self.spinner.move(
                self.width() // 2 - self.spinner.width() // 2,
                self.height() // 2 - self.spinner.height() // 2
            )

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        if self.fetcher_thread and self.fetcher_thread.isRunning():
            self.fetcher_thread.quit()
            self.fetcher_thread.wait()
        super().closeEvent(event)


class LineEditTableWidgetItem(QWidget):
    def __init__(self, readOnly):
        super(LineEditTableWidgetItem, self).__init__()
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit = QLineEdit()
        self.lineEdit.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lineEdit.setReadOnly(readOnly)
        if readOnly:
            self.lineEdit.setStyleSheet('background-color: grey;')
        self.lineEdit.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lineEdit)


class BaseTableModel(QStandardItemModel):
    def __init__(self, columns):
        super().__init__()
        self.columns = columns
        self._init_headers()

    def _init_headers(self):
        self.setHorizontalHeaderLabels(
            [item.removesuffix('.rw') if item.endswith('.rw') else item
             for item in self.columns]
        )

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        # 第一列和最后一列（操作列）特殊处理
        if index.column() == 0 or index.column() == self.columnCount() - 1:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # 检查列是否可编辑
        column_name = self.columns[index.column()]
        if column_name.endswith('.rw'):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class BaseTable(QTableView):
    def __init__(self, COLUMNS):
        super().__init__()
        self.COLUMNS = COLUMNS
        self.model = BaseTableModel(COLUMNS)
        self.setModel(self.model)

        self._init_table_properties()
        self._init_table_appearance()
        self._setup_delegates()

        # 只创建第一列的冻结视图
        self.frozenTableView = QTableView(self)
        self.frozenTableView.setModel(self.model)
        self.frozenTableView.verticalHeader().hide()

        # 只设置第一列为冻结列
        self._setup_frozen_view(self.frozenTableView, [0])

        # 连接垂直滚动信号
        self.verticalScrollBar().valueChanged.connect(
            self.frozenTableView.verticalScrollBar().setValue)

        self.updateFrozenTableGeometry()

    def _setup_frozen_view(self, view, columns):
        """设置冻结列视图的通用属性"""
        view.setFocusPolicy(Qt.NoFocus)
        view.verticalHeader().hide()
        view.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # 只显示指定列
        for i in range(self.model.columnCount()):
            if i not in columns:
                view.hideColumn(i)
            else:
                view.setColumnWidth(i, self.columnWidth(i))

        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setStyleSheet('''
            QTableView { border: none; background-color: #f0f0f0; }
        ''')

    def updateFrozenTableGeometry(self):
        """更新冻结列的几何位置"""
        if not self.model:
            return

        # 更新左侧冻结列位置
        self.frozenTableView.setGeometry(
            self.verticalHeader().width() + self.frameWidth(),
            self.frameWidth(),
            self.columnWidth(0),
            self.viewport().height() + self.horizontalHeader().height()
        )

        # 确保冻结列在最上层显示
        self.frozenTableView.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateFrozenTableGeometry()

    def moveCursor(self, cursorAction, modifiers):
        current = super().moveCursor(cursorAction, modifiers)
        if cursorAction == QAbstractItemView.MoveLeft and current.column() > 0:
            if self.visualRect(current).topLeft().x() < self.frozenTableView.columnWidth(0):
                newValue = self.horizontalScrollBar().value() + \
                    self.visualRect(current).topLeft().x() - \
                    self.frozenTableView.columnWidth(0)
                self.horizontalScrollBar().setValue(newValue)
        return current

    def scrollTo(self, index, hint=QAbstractItemView.EnsureVisible):
        if index.column() > 0:
            super().scrollTo(index, hint)

    def _init_table_properties(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def _init_table_appearance(self):
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

        # 设置列宽
        self.setColumnWidth(0, 50)

        # 调整其他列宽
        self.adjust_columns()

    def setFrozenColumn(self, column):
        """冻结指定列"""
        self.horizontalHeader().setSectionResizeMode(column, QHeaderView.Fixed)
        self.setItemDelegateForColumn(
            column, LineEditDelegate(self.COLUMNS, self))
        # 设置水平滚动条策略
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollMode(QTableView.ScrollPerPixel)

    def _setup_delegates(self):
        line_edit_delegate = LineEditDelegate(self.COLUMNS, self)
        operation_delegate = OperationDelegate(self)

        # 为每列设置适当的delegate
        for col in range(len(self.COLUMNS)):
            if col == len(self.COLUMNS) - 1:  # 最后一列（操作列）
                self.setItemDelegateForColumn(col, operation_delegate)
            else:
                self.setItemDelegateForColumn(col, line_edit_delegate)

    def adjust_columns(self, custom_widths=None):
        font_metrics = QFontMetrics(self.font())
        padding = 20

        for col in range(self.model.columnCount()):
            if custom_widths and col in custom_widths:
                width = custom_widths[col]
            else:
                header_text = self.model.headerData(col, Qt.Horizontal)
                width = font_metrics.horizontalAdvance(header_text) + padding

            if col != 0:  # 不调整第一列（已固定）
                self.setColumnWidth(col, width)

    def update_row(self, ret: bool, lane: int, row_data: dict):
        if not ret:
            print(f'dev op failed. lane:{lane}')
            return

        row = self._find_row_by_lane(lane)
        if row == -1:
            row = self.model.rowCount()
            self.model.insertRow(row)

        # 更新lane列
        self.model.setData(self.model.index(row, 0), f'lane{lane}')

        # 更新数据列
        for col, header in enumerate(self.COLUMNS[1:-1], 1):
            value_key = header.removesuffix(
                '.rw') if header.endswith('.rw') else header
            value = row_data.get(value_key)
            if value is not None:
                self.model.setData(self.model.index(row, col), str(value))

        # 为操作列创建按钮
        last_column = len(self.COLUMNS) - 1
        operation_delegate = self.itemDelegateForColumn(last_column)
        if isinstance(operation_delegate, OperationDelegate):
            editor = operation_delegate.createEditor(
                self.viewport(), None, self.model.index(row, last_column))
            self.setIndexWidget(self.model.index(row, last_column), editor)

    def _find_row_by_lane(self, lane: int) -> int:
        for row in range(self.model.rowCount()):
            if self.model.data(self.model.index(row, 0)) == f'lane{lane}':
                return row
        return -1

    def _create_dev_op_thread(self):
        raise NotImplementedError(
            "Subclasses must implement _create_dev_op_thread()")


class ConsoleWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.mainLayout = QHBoxLayout()

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.clearBtn = QToolButton()
        self.clearBtn.setToolTip('Clear console 1og')
        clearIcon = QIcon()
        clearIcon.addFile(u":/icon/image/icon/remove.ppg",
                          QSize(), QIcon.Normal, QIcon.Off)
        self.clearBtn.setIcon(clearIcon)
        self.clearBtn.setIconSize(QSize(15, 15))

        self.btnLayout = QVBoxLayout()
        self.btnLayout.addWidget(self.clearBtn)
        self.btnLayout.addWidget(QLabel())
        self.mainLayout.addLayout(self.btnLayout)
        self.mainLayout.addWidget(self.console)

        self.setLayout(self.mainLayout)

        self.bind()

    def bind(self):
        self.clearBtn.clicked.connect(self.clearConsoleLog)

    @Slot()
    def clearConsoleLog(self):
        self.console.clear()


class LineEditDelegate(QStyledItemDelegate):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.columns = columns

    def createEditor(self, parent, option, index):
        if not self._is_editable(index):
            return None

        editor = QLineEdit(parent)
        editor.setAlignment(Qt.AlignCenter)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setText(str(value) if value is not None else "")

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text(), Qt.EditRole)

    def _is_editable(self, index):
        column_name = self.columns[index.column()]
        return column_name.endswith('.rw')

    def paint(self, painter, option, index):
        if not self._is_editable(index):
            # 非可编辑单元格使用灰色背景
            option.backgroundBrush = Qt.gray
        super().paint(painter, option, index)


class OperationDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        # 创建容器widget
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)

        # 创建Get按钮
        get_btn = QToolButton(widget)
        get_btn.setText("Get")
        get_btn.clicked.connect(lambda: self._handle_get_clicked(index.row()))

        # 创建Set按钮
        set_btn = QToolButton(widget)
        set_btn.setText("Set")
        set_btn.clicked.connect(lambda: self._handle_set_clicked(index.row()))

        # 添加按钮到布局
        layout.addWidget(get_btn)
        layout.addWidget(set_btn)
        layout.addStretch()

        # 直接设置为永久widget
        self.parent().setIndexWidget(index, widget)
        return widget

    def sizeHint(self, option, index):
        return QSize(150, 35)

    def _handle_get_clicked(self, row):
        """处理Get按钮点击事件"""
        view = self.parent()
        model = view.model
        lane = int(model.data(model.index(row, 0)).replace('lane', ''))
        print(f'lane:{lane}')
        # 获取BaseFrame实例
        base_frame = self._get_base_frame(view)
        if base_frame:
            base_frame._show_loading_state()
            base_frame.fetcher_thread = base_frame._create_dev_op_thread(
                'get', lane)
            base_frame.fetcher_thread.row_ready.connect(view.update_row)
            base_frame.fetcher_thread.log_message.connect(
                base_frame.consoleWidget.console.appendPlainText)
            base_frame.fetcher_thread.finished.connect(
                base_frame._hide_loading_state)
            base_frame.fetcher_thread.start()

    def _handle_set_clicked(self, row):
        """处理Set按钮点击事件"""
        view = self.parent()
        model = view.model

        # 收集可编辑列的数据
        row_data = {}
        for col, header in enumerate(view.COLUMNS[1:-1], 1):
            if header.endswith('.rw'):
                value = model.data(model.index(row, col))
                if value:  # 只收集非空值
                    row_data[header.removesuffix('.rw')] = value

        lane = int(model.data(model.index(row, 0)).replace('lane', ''))

        # 获取BaseFrame实例
        base_frame = self._get_base_frame(view)
        if base_frame:
            base_frame._show_loading_state()
            base_frame.fetcher_thread = base_frame._create_dev_op_thread(
                'set', lane, row_data)
            base_frame.fetcher_thread.row_ready.connect(view.update_row)
            base_frame.fetcher_thread.log_message.connect(
                base_frame.consoleWidget.console.appendPlainText)
            base_frame.fetcher_thread.finished.connect(
                base_frame._hide_loading_state)
            base_frame.fetcher_thread.start()

    def _get_base_frame(self, widget):
        """获取BaseFrame实例的辅助方法"""
        parent = widget.parent()
        while parent and not isinstance(parent, BaseFrame):
            parent = parent.parent()
        return parent
