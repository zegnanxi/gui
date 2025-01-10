from PySide6.QtWidgets import (
    QHeaderView, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPlainTextEdit, QToolButton, QSplitter, QTableView)
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem, QFontMetrics, QFont
from PySide6.QtCore import Qt, QSize, Slot

from .progress_indicator import QProgressIndicator
from .delegates import (
    LineEditDelegate,
    SwitchButtonDelegate,
    OperationDelegate,
    CheckboxDelegate,
    ComboBoxDelegate
)


class BaseFrame(QWidget):
    @staticmethod
    def _process_columns(columns, side):
        results = []
        for item in columns:
            # 检查是否有side属性
            if isinstance(item, dict) and 'side' in item:
                # 如果指定了side且匹配当前side，则添加
                if item['side'] == side:
                    results.append(item)
            else:
                # 对于没有side属性的项目，直接添加
                results.append(item)
        return results

    def __init__(self, side: str, model: str, table_properties: dict = None):
        super().__init__()
        self.fetcher_thread = None
        self._init_ui(side, model, table_properties)
        self._init_connections()

    def _init_ui(self, side: str, model: str, table_properties: dict):
        self.spinner = self._create_spinner()
        self.consoleWidget = ConsoleWidget()
        self.tableWidget = BaseTable(self.COLUMNS, table_properties)

        font = QFont()
        font.setBold(True)
        label = QLabel(f'{side} - {model}')
        label.setFont(font)

        upperLayout = QVBoxLayout()
        upperLayout.addWidget(label)
        upperLayout.addWidget(self.tableWidget)

        upperWidget = QWidget()
        upperWidget.setLayout(upperLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._create_splitter(upperWidget, self.consoleWidget))
        self.setLayout(mainLayout)

    def _create_spinner(self):
        spinner = QProgressIndicator(self)
        spinner.hide()
        return spinner

    def _create_splitter(self, upperWidget, lowerWidget):
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(upperWidget)
        splitter.addWidget(lowerWidget)
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

        self.show_loading_state()

        # 创建并启动新的数据获取线程
        self.fetcher_thread = self.create_dev_op_thread()
        if self.fetcher_thread:
            self.fetcher_thread.row_ready.connect(
                self.tableWidget.update_row)
            self.fetcher_thread.log_message.connect(
                self.consoleWidget.console.appendPlainText)
            self.fetcher_thread.finished.connect(
                self._hide_loading_state)
            self.fetcher_thread.start()

    def show_loading_state(self):
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
        main_window.setEnabled(False)

    def _hide_loading_state(self):
        """隐藏加载状态"""
        self.spinner.stop()
        self.spinner.hide()
        self.window().setEnabled(True)

    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        if self.spinner and not self.spinner.isHidden():
            self.spinner.move(
                self.width() // 2 - self.spinner.width() // 2,
                self.height() // 2 - self.spinner.height() // 2
            )

    def setup_delegates(self):
        """设置各列的delegate"""
        for col, delegate_info in self.delegates_map.items():
            delegate_type = delegate_info.get('type')
            prop = delegate_info.get('prop', {})

            if delegate_type == 'line_edit':
                self.setItemDelegateForColumn(col, LineEditDelegate(self, prop))
            elif delegate_type == 'switch':
                self.setItemDelegateForColumn(col, SwitchButtonDelegate(self))
            elif delegate_type == 'operation':
                self.setItemDelegateForColumn(col, OperationDelegate(self))
            elif delegate_type == 'checkbox':
                self.setItemDelegateForColumn(col, CheckboxDelegate(self))
            elif delegate_type == 'combobox':
                self.setItemDelegateForColumn(col, ComboBoxDelegate(self, prop))


class BaseTableModel(QStandardItemModel):
    def __init__(self, columns):
        super().__init__()
        self.setHorizontalHeaderLabels([item['index'] for item in columns])

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        # 检查列是否可编辑
        # column_info = self.columns[index.column()]
        # if isinstance(column_info, dict) and column_info.get('editable', False):
        #     return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class BaseTable(QTableView):
    def __init__(self, columns, table_properties: dict):
        super().__init__()
        # 移除第一列后的列定义
        self.columns = columns[1:]
        self.model = BaseTableModel(self.columns)
        self._init_table(table_properties)
        self._apply_styles()

    def _apply_styles(self):
        # 设置表格整体样式
        self.setStyleSheet("""
            QTableView {
                background-color: #FFFFFF;
                gridline-color: #E0E0E0;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                selection-background-color: #E8F0FE;
                selection-color: #000000;
            }

            QTableView::item:selected {
                background-color: #E8F0FE;
                color: #000000;
            }

            QTableView::item:focus {
                background-color: #E8F0FE;
                border: none;
                color: #000000;
            }

            QTableView::item {
                background-color: #FFFFFF;
                border: none;
                margin: 1px;
                alignment: center;
            }

            QHeaderView {
                background-color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 6px;
                border: none;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
                color: #444444;
            }

            QHeaderView::section:vertical {
                background-color: #F8F9FA;
                border-right: 1px solid #D0D0D0;
            }

            QHeaderView::section:horizontal {
                background-color: #DADCE0;
                border-right: 1px solid #FFFFFF;
                border-left: 1px solid #FFFFFF;
            }

            QTableCornerButton::section {
                background-color: #DADCE0;
                border-right: 1px solid #FFFFFF;
            }
        """)

    def _adjust_columns(self):
        """调整表格列宽"""
        minimum_width = 80
        header = self.horizontalHeader()
        font_metrics = QFontMetrics(self.font())
        padding = 25

        # 获取stretch模式设置
        stretch_mode = (self.table_properties or {}).get('strech', False)

        for column in range(self.model.columnCount()):
            column_info = self.columns[column]

            # 检查是否有预定义宽度（从column_info或custom_widths中获取）
            if isinstance(column_info, dict) and 'width' in column_info:
                width = column_info['width']
                header.setSectionResizeMode(column, QHeaderView.Fixed)
            else:
                if stretch_mode:
                    header.setSectionResizeMode(column, QHeaderView.Stretch)
                    continue

                # 获取表头文字宽度
                header_text = self.model.headerData(column, Qt.Horizontal)
                width = (font_metrics.horizontalAdvance(str(header_text)) + padding) if header_text else minimum_width
                header.setSectionResizeMode(column, QHeaderView.Fixed)

            # 设置列宽（仅对Fixed模式的列）
            self.setColumnWidth(column, max(width, minimum_width))

    def _init_table(self, table_properties: dict):
        self.setModel(self.model)
        self.table_properties = table_properties  # 存储table_properties以供后续使用
        self._setup_table_properties(table_properties)
        self._setup_delegates()
        self._setup_selection_handling()

        # 调整列宽
        self._adjust_columns()

    def _setup_table_properties(self, table_properties: dict):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setHorizontalScrollMode(QTableView.ScrollPerPixel)

        # 显示垂直表头并设置其属性
        v_header = self.verticalHeader()
        v_header.setVisible(True)
        v_header.setDefaultAlignment(Qt.AlignCenter)
        v_header.setHighlightSections(False)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        v_header.setDefaultSectionSize(40)  # 行高40
        v_header.setMinimumWidth(60)

        # 设置表头属性
        header = self.horizontalHeader()
        # header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setHighlightSections(False)
        header.setFixedHeight(25)  # 设置水平表头高度为30
        header.setMinimumWidth(100)

        # 设置表格属性
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        self.setAlternatingRowColors(False)
        self.setWordWrap(False)
        self.setCornerButtonEnabled(False)

        # 设置选择行为
        self.setSelectionMode(QTableView.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectRows)

        # 添加以下设置来禁用自动滚动
        self.setAutoScroll(False)
        self.setFocusPolicy(Qt.NoFocus)

    def _setup_delegates(self):
        # 为每列设置适当的delegate
        self.setItemDelegateForColumn(len(self.columns) - 1, OperationDelegate(self))

        for col, column_info in enumerate(self.columns[:-1]):
            column_type = column_info.get('type', 'int')
            if column_type == 'boolean':
                self.setItemDelegateForColumn(col, SwitchButtonDelegate(self, prop=column_info))
            elif column_type == 'checkbox':
                self.setItemDelegateForColumn(col, CheckboxDelegate(self, prop=column_info))
            elif column_type == 'select':
                self.setItemDelegateForColumn(col, ComboBoxDelegate(self, prop=column_info))
            else:
                self.setItemDelegateForColumn(col, LineEditDelegate(self, prop=column_info))

    def _update_row_data(self, row: int, lane: int, row_data: dict):
        for col, column_info in enumerate(self.columns[0:-1]):
            # 获取值的键名
            value_key = column_info['index'] if isinstance(column_info, dict) else column_info
            value_key = value_key.removesuffix('.rw')

            value = row_data.get(value_key)
            if value is not None:
                # 设置数据值
                self.model.setData(self.model.index(row, col), str(value))
                self.model.setData(self.model.index(row, col), Qt.AlignCenter, Qt.TextAlignmentRole)

                data_delegate = self.itemDelegateForColumn(col)
                editor = self.indexWidget(self.model.index(row, col))
                if editor is None:
                    editor = data_delegate.createEditor(self.viewport(), None, self.model.index(row, col))
                    self.setIndexWidget(self.model.index(row, col), editor)
                data_delegate.setEditorData(editor, self.model.index(row, col))

        last_column = len(self.columns) - 1
        last_index = self.model.index(row, last_column)
        editor = self.indexWidget(last_index)
        if editor is None:
            operation_delegate = self.itemDelegateForColumn(last_column)
            if isinstance(operation_delegate, OperationDelegate):
                editor = operation_delegate.createEditor(self.viewport(), None, last_index)
                self.setIndexWidget(last_index, editor)
            else:
                raise ValueError(f'operation_delegate is not OperationDelegate: {operation_delegate}')

    def update_row(self, ret: bool, lane: int, row_data: dict):
        if not ret:
            raise ValueError(f'device operation failed, lane:{lane}')

        row = self._find_or_create_row(lane)
        self._update_row_data(row, lane, row_data)

        # 更新所有列的可编辑状态
        self.update_editable_states(row)

    def _find_or_create_row(self, lane: int) -> int:
        for row in range(self.model.rowCount()):
            if self.model.verticalHeaderItem(row).text() == f'lane{lane}':
                return row

        row = self.model.rowCount()
        self.model.insertRow(row)
        self.model.setVerticalHeaderItem(row, QStandardItem(f'lane{lane}'))
        return row

    def create_dev_op_thread(self):
        raise NotImplementedError("Subclasses must implement create_dev_op_thread()")

    def _setup_selection_handling(self):
        """设置选择变化的处理"""
        def on_selection_changed(selected, deselected):
            # 更新所有可见编辑器的背景色
            for row in range(self.model.rowCount()):
                for col in range(self.model.columnCount()):
                    index = self.model.index(row, col)
                    editor = self.indexWidget(index)
                    delegate = self.itemDelegateForColumn(col)
                    if hasattr(delegate, 'updateBackground'):
                        delegate.updateBackground(editor, index)

        self.selectionModel().selectionChanged.connect(on_selection_changed)

    def update_editable_states(self, row):
        """更新行中所有列的可编辑状态"""
        for col, column_info in enumerate(self.columns[:-1]):
            if isinstance(column_info.get('editable'), dict):
                index = self.model.index(row, col)
                editor = self.indexWidget(index)
                if editor:
                    delegate = self.itemDelegateForColumn(col)
                    is_editable = self.check_editable(col, row)

                    # 使用新的方法设置只读状态
                    if hasattr(delegate, 'setEditorReadOnly'):
                        delegate.setEditorReadOnly(editor, not is_editable)

                    # 更新背景色
                    if hasattr(delegate, 'updateBackground'):
                        delegate.updateBackground(editor, index)

    def check_editable(self, column_index, row_index):
        """检查单元格是否可编辑的通用方法"""
        column_info = self.columns[column_index]
        editable = column_info.get('editable', False)

        if isinstance(editable, dict):
            # 遍历所有的条件
            for dep_column, allowed_values in editable.items():
                # 查找依赖列的索引
                dep_col_idx = self._find_column_index(dep_column)
                if dep_col_idx is None:
                    continue

                # 获取依赖列的值
                dep_value = self.model.data(self.model.index(row_index, dep_col_idx))

                # 根据allowed_values中第一个值的类型来决定如何转换dep_value
                if allowed_values:
                    target_type = type(allowed_values[0])
                    try:
                        if target_type == int:
                            dep_value = int(dep_value)
                        elif target_type == float:
                            dep_value = float(dep_value)
                        elif target_type == str:
                            dep_value = str(dep_value)

                        if dep_value not in allowed_values:
                            return False
                    except (ValueError, TypeError):
                        return False

            return True
        return bool(editable)

    def _find_column_index(self, column_name):
        """查找列名对应的索引"""
        for idx, col_info in enumerate(self.columns):
            if isinstance(col_info, dict) and col_info.get('index') == column_name:
                return idx
        return None


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

    @ Slot()
    def clearConsoleLog(self):
        self.console.clear()
