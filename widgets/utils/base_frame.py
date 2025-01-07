from PySide6.QtWidgets import (
    QTableWidget, QHeaderView, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QPlainTextEdit, QToolButton, QSplitter)
from PySide6.QtGui import QFontMetrics, QIcon
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

        self.tableWidget.setRowCount(0)
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


class BaseTable(QTableWidget):
    def __init__(self, COLUMNS):
        super().__init__()
        self.COLUMNS = COLUMNS
        self._init_table_properties()
        self._init_table_appearance()

    def _init_table_properties(self):
        """初始化表格基本属性"""
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(
            [item.removesuffix('.rw') if item.endswith('.rw') else item for item in self.COLUMNS])
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _init_table_appearance(self):
        """初始化表格外观"""
        self.verticalHeader().setVisible(False)

        # 设置表头
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

        # 调整列宽
        COLUMN_WIDTHS = {
            0: 50,   # lane列
            len(self.COLUMNS) - 1: 150   # 操作列
        }
        self.adjust_columns(COLUMN_WIDTHS)

    def adjust_columns(self, custom_widths=None):
        """
        调整表格列宽：
        - 所有列默认根据表头文字长度设置宽度
        - custom_widths中指定的列使用固定宽度
        """
        header = self.horizontalHeader()
        font_metrics = QFontMetrics(self.font())
        padding = 20  # 文字两侧的padding

        for column in range(self.columnCount()):
            if custom_widths and column in custom_widths:
                # 使用指定的固定宽度
                width = custom_widths[column]
            else:
                # 根据表头文字计算宽度
                header_item = self.horizontalHeaderItem(column)
                if header_item:
                    header_text = header_item.text()
                    width = font_metrics.horizontalAdvance(
                        header_text) + padding

            header.setSectionResizeMode(column, QHeaderView.Fixed)
            self.setColumnWidth(column, width)

    def update_row(self, ret: bool, lane: int, row_data: dict):
        """更新或插入一行数据"""
        if ret is False:
            print(f'dev op failed. lane:{lane}')
            return

        existing_row = -1
        for row in range(self.rowCount()):
            if self.cellWidget(row, 0) and self.cellWidget(row, 0).text() == f'lane{lane}':
                existing_row = row
                break

        if existing_row >= 0:
            self._update_row_data(existing_row, row_data)
        else:
            new_row = self.rowCount()
            self.insertRow(new_row)
            self._update_row_data(new_row, row_data)
            self._add_operation_buttons(new_row, len(self.COLUMNS) - 1)

    def _update_row_data(self, row: int, values: dict):
        """更新行数据"""
        lane = QLabel(f'lane{row}')
        lane.setAlignment(Qt.AlignCenter)
        self.setCellWidget(row, 0, lane)

        for col, header in enumerate(self.COLUMNS[1:-1], 1):
            value_key = header
            is_editable = header.endswith('.rw')
            if is_editable:
                value_key = header.removesuffix('.rw')

            value = values.get(value_key)
            if value is not None:
                item = LineEditTableWidgetItem(not is_editable)
                item.lineEdit.setText(str(value))
                self.setCellWidget(row, col, item)

    def _add_operation_buttons(self, row: int, col: int):
        """添加操作按钮"""
        operation_widget = QWidget()
        layout = QHBoxLayout(operation_widget)
        layout.setContentsMargins(5, 2, 5, 2)

        get_btn = QPushButton("Get")
        set_btn = QPushButton("Set")

        get_btn.clicked.connect(lambda: self.on_get_clicked(row))
        set_btn.clicked.connect(lambda: self.on_set_clicked(row))

        layout.addWidget(get_btn)
        layout.addWidget(set_btn)
        self.setCellWidget(row, col, operation_widget)

    def _create_dev_op_thread(self):
        raise NotImplementedError(
            "Subclasses must implement _create_dev_op_thread()")

    def on_get_clicked(self, row):
        id_item: QLabel = self.cellWidget(row, 0)
        if id_item:
            row_id = id_item.text()
            lane = int(row_id.replace('lane', ''))

            # 修改获取父窗口的方法
            parent = self.parent()
            while parent and not isinstance(parent, BaseFrame):
                parent = parent.parent()

            if parent and isinstance(parent, BaseFrame):
                parent._show_loading_state()
                parent.fetcher_thread = parent._create_dev_op_thread(
                    'get', lane)
                parent.fetcher_thread.row_ready.connect(self.update_row)
                parent.fetcher_thread.log_message.connect(
                    parent.consoleWidget.console.appendPlainText)
                parent.fetcher_thread.finished.connect(
                    parent._hide_loading_state)
                parent.fetcher_thread.start()

    def on_set_clicked(self, row):
        # 获取当前行的所有数据
        row_data = {}
        id_item: QLabel = self.cellWidget(row, 0)
        if id_item:
            # 从第二列开始获取数据（跳过lane列）
            for col, header in enumerate(self.COLUMNS[1:-1], 1):
                item: LineEditTableWidgetItem = self.cellWidget(row, col)
                if item and header.endswith('.rw'):
                    row_data[header.removesuffix('.rw')] = item.lineEdit.text()

            row_id = id_item.text()
            lane = int(row_id.replace('lane', ''))

            # 修改获取父窗口的方法
            parent = self.parent()
            while parent and not isinstance(parent, BaseFrame):
                parent = parent.parent()

            if parent and isinstance(parent, BaseFrame):
                parent._show_loading_state()
                parent.fetcher_thread = parent._create_dev_op_thread(
                    'set', lane, row_data)
                parent.fetcher_thread.row_ready.connect(self.update_row)
                parent.fetcher_thread.log_message.connect(
                    parent.consoleWidget.console.appendPlainText)
                parent.fetcher_thread.finished.connect(
                    parent._hide_loading_state)
                parent.fetcher_thread.start()


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
