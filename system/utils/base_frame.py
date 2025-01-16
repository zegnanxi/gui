from PySide6.QtWidgets import (
    QHeaderView, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPlainTextEdit, QToolButton, QSplitter, QTableView)
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem, QFontMetrics, QFont
from PySide6.QtCore import Qt, QSize, Slot, QModelIndex

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

    def __init__(self, side: str, model: str, table_properties: dict = {}):
        # 设置默认值
        default_properties = {
            'horizontal': True,         # 默认水平布局
            'strech': False,            # 默认不拉伸
            'row_select': True,         # 默认允许行选择
            'spliter_size': [200, 100]  # 默认分割器尺寸
        }
        # 使用默认值更新传入的属性
        self.table_properties = default_properties.copy()
        self.table_properties.update(table_properties)

        super().__init__()
        self.fetcher_thread = None
        self._init_ui(side, model)
        self._init_connections()

    def _init_ui(self, side: str, model: str):
        self.spinner = self._create_spinner()
        self.consoleWidget = ConsoleWidget()
        self.tableWidget = BaseTable(self.COLUMNS, self.table_properties)

        font = QFont()
        font.setBold(True)
        label = QLabel(f'{side} - {model}:')
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
        splitter.setSizes(self.table_properties.get('spliter_size'))
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
        if self.table_properties.get('horizontal'):
            self.tableWidget.model.setRowCount(0)
        else:
            self.tableWidget.model.setColumnCount(0)
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


class BaseTableModel(QStandardItemModel):
    def __init__(self, columns, horizontal: bool):
        super().__init__()
        bold_font = QFont()
        bold_font.setBold(True)

        # 设置表头标签并应用粗体字体
        for col, item in enumerate(columns):
            header_item = QStandardItem(item['index'])
            header_item.setFont(bold_font)
            if horizontal:
                self.setHorizontalHeaderItem(col, header_item)
            else:
                self.setVerticalHeaderItem(col, header_item)

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
        # 检查是否有垂直表头配置
        self.vertical_header_config = next((col for col in columns if col.get('type') == 'vertical header'), None)
        # 移除垂直表头配置后的列定义
        self.columns = [col for col in columns if col != self.vertical_header_config]
        self.model: BaseTableModel = BaseTableModel(self.columns, table_properties.get('horizontal'))
        self._init_table(table_properties)
        self._apply_styles()

    def _apply_styles(self):
        # 设置表格整体样式
        self.setStyleSheet("""
            QTableView {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }

            QTableView::item:selected {
                background-color: #E8F0FE;
            }

            QHeaderView {
                background-color: #FFFFFF;
            }

            QHeaderView::section:vertical {
                background-color: #FFFFFF;
                border: none;
                border-right: 1px solid #E0E0E0;
                border-bottom: 1px solid #E0E0E0;
                margin-bottom: 0px;
            }

            QTableCornerButton::section {
                border-bottom: 1px solid #E0E0E0;
                margin-bottom: 0px;
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
        self._setup_delegates(table_properties.get('horizontal'))
        self._setup_selection_handling()

        # 调整列宽
        if table_properties.get('horizontal'):
            self._adjust_columns()

    def _setup_table_properties(self, table_properties: dict):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if table_properties.get('horizontal'):
            self.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        else:
            self.setVerticalScrollMode(QTableView.ScrollPerPixel)

        # 根据配置显示或隐藏垂直表头
        v_header = self.verticalHeader()
        if self.vertical_header_config or not table_properties.get('horizontal'):
            v_header.setVisible(True)
            v_header.setDefaultAlignment(Qt.AlignCenter)
            v_header.setHighlightSections(False)
            v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            v_header.setDefaultSectionSize(40)
            v_header.setMinimumWidth(60)
        else:
            v_header.setVisible(False)
            v_header.setDefaultSectionSize(40)

        # 设置表头属性
        header = self.horizontalHeader()
        # header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setHighlightSections(False)
        header.setMinimumWidth(100)

        # 添加corner button的设置
        self.setCornerButtonEnabled(False)
        # corner_button = QLabel(self.vertical_header_config.get("index", ""))
        # corner_button.setAlignment(Qt.AlignCenter)
        # self.setCornerButtonEnabled(True)
        # self.setCornerWidget(corner_button)

        # 设置表格属性
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        self.setAlternatingRowColors(False)
        self.setWordWrap(False)

        # 设置选择行为
        if table_properties.get('row_select'):
            self.setSelectionMode(QTableView.SingleSelection)
            if table_properties.get('horizontal'):
                self.setSelectionBehavior(QTableView.SelectRows)
            else:
                self.setSelectionBehavior(QTableView.SelectColumns)
        else:
            self.setSelectionMode(QTableView.NoSelection)  # 禁用选择功能

        # 添加以下设置来禁用自动滚动
        self.setAutoScroll(False)
        self.setFocusPolicy(Qt.NoFocus)

    def _setup_delegates(self, horizontal: bool):
        # 根据表格方向选择代理设置函数
        set_delegate = self.setItemDelegateForColumn if horizontal else self.setItemDelegateForRow

        # 设置最后一列/行的操作代理
        set_delegate(len(self.columns) - 1, OperationDelegate(self, prop=self.columns[-1], horizontal=horizontal))

        # 设置其他列/行的代理
        for idx, column_info in enumerate(self.columns[:-1]):
            column_type = column_info.get('type', 'int')
            delegate = {
                'boolean': lambda: SwitchButtonDelegate(self, prop=column_info),
                'checkbox': lambda: CheckboxDelegate(self, prop=column_info),
                'select': lambda: ComboBoxDelegate(self, prop=column_info)
            }.get(column_type, lambda: LineEditDelegate(self, prop=column_info))()

            set_delegate(idx, delegate)

    def _get_index(self, row: int, col: int):
        if self.table_properties.get('horizontal'):
            return self.model.index(row, col)
        else:
            return self.model.index(col, row)

    def _get_delegate(self, col: int):
        if self.table_properties.get('horizontal'):
            return self.itemDelegateForColumn(col)
        else:
            return self.itemDelegateForRow(col)

    def _update_row_data(self, row: int, lane: int, row_data: dict):
        for col, column_info in enumerate(self.columns[0:-1]):
            value = row_data.get(column_info['index'])
            if value is not None:
                index = self._get_index(row, col)
                data_delegate = self._get_delegate(col)

                self.model.setData(index, value)
                self.model.setData(index, Qt.AlignCenter, Qt.TextAlignmentRole)
                editor = self.indexWidget(index)
                if editor is None:
                    editor = data_delegate.createEditor(self.viewport(), None, index)
                    self.setIndexWidget(index, editor)
                data_delegate.setEditorData(editor, index)

        last_column = len(self.columns) - 1
        last_index = self._get_index(row, last_column)
        editor = self.indexWidget(last_index)
        if editor is None:
            operation_delegate = self._get_delegate(last_column)
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

    def _find_or_create_row(self, lane: int) -> int:
        if self.vertical_header_config:
            target_row = f'{self.vertical_header_config["index"]}{lane}'
        else:
            target_row = str(lane)

        if self.table_properties.get('horizontal'):
            for row in range(self.model.rowCount()):
                if self.model.verticalHeaderItem(row).text() == target_row:
                    return row

            row = self.model.rowCount()
            self.model.insertRow(row)
            self.model.setVerticalHeaderItem(row, QStandardItem(target_row))
            return row
        else:
            for row in range(self.model.columnCount()):
                if self.model.horizontalHeaderItem(row).text() == target_row:
                    return row

            row = self.model.columnCount()
            self.model.insertColumn(row)
            self.model.setHorizontalHeaderItem(row, QStandardItem(target_row))
            return row

    def create_dev_op_thread(self):
        raise NotImplementedError("Subclasses must implement create_dev_op_thread()")

    def _setup_selection_handling(self):
        """设置选择变化的处理"""
        def on_selection_changed(selected, deselected):
            # 更新编辑器背景色
            for row in range(self.model.rowCount()):
                for col in range(self.model.columnCount()):
                    if self.table_properties.get('horizontal'):
                        delegate = self.itemDelegateForColumn(col)
                    else:
                        delegate = self.itemDelegateForRow(row)
                    if hasattr(delegate, 'updateBackground'):
                        index = self.model.index(row, col)
                        editor = self.indexWidget(index)
                        delegate.updateBackground(editor, index)

        self.selectionModel().selectionChanged.connect(on_selection_changed)

    def update_one_line_editable_states(self, row, col):
        for prop_index, column_info in enumerate(self.columns[:-1]):
            if not isinstance(column_info.get('editable'), dict):
                continue

            if self.table_properties.get('horizontal'):
                index = self.model.index(row, prop_index)
                delegate = self.itemDelegateForColumn(prop_index)
            else:
                index = self.model.index(prop_index, col)
                delegate = self.itemDelegateForRow(prop_index)

            editor = self.indexWidget(index)
            if editor and hasattr(delegate, 'setEditorReadOnly'):
                delegate.setEditorReadOnly(editor, not self.check_editable(index))

            if editor and hasattr(delegate, 'updateBackground'):
                delegate.updateBackground(editor, index)

    def check_editable(self, index: QModelIndex):
        if self.table_properties.get('horizontal'):
            prop_index = index.column()
        else:
            prop_index = index.row()

        editable = self.columns[prop_index].get('editable', False)

        if not isinstance(editable, dict):
            return bool(editable)

        for dep_column, allowed_values in editable.items():
            # 查找依赖列的索引
            dep_idx = self._find_column_index(dep_column)
            if dep_idx is None:
                return False

            if self.table_properties.get('horizontal'):
                dep_value = self.model.data(self.model.index(index.row(), dep_idx))
            else:
                dep_value = self.model.data(self.model.index(dep_idx, index.column()))

            if allowed_values and dep_value not in allowed_values:
                return False

        return True

    def _find_column_index(self, column_name):
        """查找列名对应的索引"""
        for idx, col_info in enumerate(self.columns):
            if col_info.get('index') == column_name:
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
        clearIcon.addFile(u":/icon/image/icon/remove.png", QSize(), QIcon.Normal, QIcon.Off)
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
