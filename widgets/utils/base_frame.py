from PySide6.QtWidgets import (
    QHeaderView, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QToolButton, QSplitter, QTableView, QStyledItemDelegate)
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
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
        self.fetcher_thread = None
        self._init_ui()
        self._init_connections()

    def _init_ui(self):
        self.mainLayout = QVBoxLayout()
        self.spinner = self._create_spinner()
        self.consoleWidget = ConsoleWidget()
        self.tableWidget = BaseTable(self.COLUMNS)

        self.splitter = self._create_splitter()
        self.mainLayout.addWidget(self.splitter)
        self.setLayout(self.mainLayout)

    def _create_spinner(self):
        spinner = QProgressIndicator(self)
        spinner.hide()
        return spinner

    def _create_splitter(self):
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(self.tableWidget)
        splitter.addWidget(self.consoleWidget)
        splitter.setSizes([200, 100])
        return splitter

    def _init_connections(self):
        if self.fetcher_thread:
            self.fetcher_thread.row_ready.connect(self.tableWidget.update_row)
            self.fetcher_thread.log_message.connect(
                self.consoleWidget.console.appendPlainText)
            self.fetcher_thread.finished.connect(self._hide_loading_state)

    def load_data(self):
        """基类的数据加载方法"""
        # 如果已有正在运行的线程，先停止它
        if self.fetcher_thread and self.fetcher_thread.isRunning():
            self.fetcher_thread.quit()
            self.fetcher_thread.wait()

        # 清除表格数据
        self.tableWidget.model.setRowCount(0)
        # 清除控制台日志
        self.consoleWidget.clearConsoleLog()

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

    def data(self, index, role=Qt.DisplayRole):
        # 添加对齐角色的处理
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return super().data(index, role)

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
    def __init__(self, columns):
        super().__init__()
        self.columns = columns
        self.model = BaseTableModel(columns[1:])
        self._init_table()
        self._apply_styles()

    def _apply_styles(self):
        # 设置表格整体样式
        self.setStyleSheet("""
            QTableView {
                background-color: #ffffff;
                gridline-color: #e0e0e0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                selection-background-color: #e8f0fe;
                selection-color: #000000;
            }

            QTableView::item {
                padding: 5px;
                border: none;
                alignment: center;
            }

            QHeaderView {
                background-color: #ffffff;
            }

            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 6px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                color: #444444;
            }

            QHeaderView::section:vertical {
                background-color: #f8f9fa;
                border-right: 1px solid #d0d0d0;
            }

            QHeaderView::section:horizontal {
                background-color: #f8f9fa;
            }

            /* 添加左上角单元格样式 */
            QTableCornerButton::section {
                background-color: #f8f9fa;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
            }
        """)

    def _init_table(self):
        self.setModel(self.model)
        self._setup_table_properties()
        self._setup_delegates()

        header = self.horizontalHeader()
        for i in range(self.model.columnCount() - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            # self.model.setHeaderData(i, Qt.Horizontal, Qt.AlignCenter, Qt.TextAlignmentRole)

        # 最后一列（操作列）保持固定宽度
        header.setSectionResizeMode(self.model.columnCount() - 1, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(self.model.columnCount() - 1, 200)

    def _setup_table_properties(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setHorizontalScrollMode(QTableView.ScrollPerPixel)

        # 显示垂直表头并设置其属性
        self.verticalHeader().setVisible(True)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.verticalHeader().setDefaultSectionSize(40)  # 将行高从30增加到40
        self.verticalHeader().setMinimumWidth(80)  # 设置最小宽度

        header = self.horizontalHeader()
        # header.setStretchLastSection(True)

        # 设置表格属性
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        self.setAlternatingRowColors(True)
        self.setWordWrap(False)
        self.setCornerButtonEnabled(False)

        # 设置表头属性
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setHighlightSections(False)

        v_header = self.verticalHeader()
        v_header.setDefaultAlignment(Qt.AlignCenter)
        v_header.setHighlightSections(False)
        v_header.setMinimumWidth(60)
        v_header.setMaximumWidth(80)

        # 设置选择行为
        self.setSelectionMode(QTableView.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectRows)

    def _setup_delegates(self):
        line_edit_delegate = LineEditDelegate(self.columns, self)
        operation_delegate = OperationDelegate(self)

        # 为每列设置适当的delegate
        for col in range(len(self.columns) - 1):
            if col == len(self.columns) - 2:  # 最后一列（操作列）
                self.setItemDelegateForColumn(col, operation_delegate)
            else:
                self.setItemDelegateForColumn(col, line_edit_delegate)

    def _update_row_data(self, row: int, lane: int, row_data: dict):
        # # 更新lane列
        # self.model.setData(self.model.index(row, 0), f'lane{lane}')

        # 更新数据列
        for col, header in enumerate(self.columns[1:-1], 1):
            value_key = header.removesuffix(
                '.rw') if header.endswith('.rw') else header
            value = row_data.get(value_key)
            if value is not None:
                self.model.setData(self.model.index(row, col - 1), str(value))

        # 为操作列创建按钮
        last_column = len(self.columns) - 2
        operation_delegate = self.itemDelegateForColumn(last_column)
        if isinstance(operation_delegate, OperationDelegate):
            editor = operation_delegate.createEditor(
                self.viewport(), None, self.model.index(row, last_column))
            self.setIndexWidget(self.model.index(row, last_column), editor)
        else:
            raise ValueError(f'operation_delegate is not OperationDelegate: {
                             operation_delegate}')

    def update_row(self, ret: bool, lane: int, row_data: dict):
        try:
            if not ret:
                raise ValueError(f'device operation failed, lane:{lane}')

            row = self._find_or_create_row(lane)
            self._update_row_data(row, lane, row_data)
            # 设置垂直表头的文本
            self.model.setVerticalHeaderItem(row, QStandardItem(f'lane{lane}'))

        except Exception as e:
            raise e

    def _find_or_create_row(self, lane: int) -> int:
        row = self._find_row_by_lane(lane)
        if row == -1:
            row = self.model.rowCount()
            self.model.insertRow(row)
        return row

    def _find_row_by_lane(self, lane: int) -> int:
        for row in range(self.model.rowCount()):
            if self.model.verticalHeaderItem(row).text() == f'lane{lane}':
                return row
        return -1

    def _create_dev_op_thread(self):
        raise NotImplementedError(
            "Subclasses must implement _create_dev_op_thread()")


class ConsoleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._init_connections()

    def _init_ui(self):
        self.mainLayout = QHBoxLayout()
        self.console = self._create_console()
        self.clearBtn = self._create_clear_button()
        self._setup_layout()

    def _create_console(self):
        console = QPlainTextEdit()
        console.setReadOnly(True)
        return console

    def _create_clear_button(self):
        clearBtn = QToolButton()
        clearBtn.setToolTip('Clear console log')
        clearIcon = QIcon()
        clearIcon.addFile(u":/icon/image/icon/remove.ppg",
                          QSize(), QIcon.Normal, QIcon.Off)
        clearBtn.setIcon(clearIcon)
        clearBtn.setIconSize(QSize(15, 15))
        return clearBtn

    def _setup_layout(self):
        btnLayout = QVBoxLayout()
        btnLayout.addWidget(self.clearBtn)
        btnLayout.addWidget(QLabel())
        self.mainLayout.addLayout(btnLayout)
        self.mainLayout.addWidget(self.console)
        self.setLayout(self.mainLayout)

    def _init_connections(self):
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
        editor.setStyleSheet("""
            QLineEdit {
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 2px 4px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #007AFF;
            }
        """)
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
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        # 修改按钮样式和大小策略
        get_btn = QToolButton(widget)
        get_btn.setText("Get")
        get_btn.clicked.connect(lambda: self._handle_get_clicked(index.row()))
        get_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        get_btn.setFixedHeight(24)
        # 创建Set按钮
        set_btn = QToolButton(widget)
        set_btn.setText("Set")
        set_btn.clicked.connect(lambda: self._handle_set_clicked(index.row()))
        set_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        set_btn.setFixedHeight(24)
        # 添加按钮到布局
        layout.addWidget(get_btn, 1)
        layout.addWidget(set_btn, 1)
        layout.addStretch()

        widget.setStyleSheet("""
            QToolButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                min-width: 60px;
                height: 24px;
            }
            QToolButton:hover {
                background-color: #808080;
            }
            QToolButton:pressed {
                background-color: #4d4d4d;
            }
        """)

        return widget

    def sizeHint(self, option, index):
        return QSize(180, 32)

    def _handle_get_clicked(self, row):
        """处理Get按钮点击事件"""
        view = self.parent()
        model = view.model
        lane = int(model.data(model.index(row, 0)).replace('lane', ''))
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
        for col, header in enumerate(view.columns[1:-1], 1):
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
