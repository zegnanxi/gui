from PySide6.QtWidgets import (
    QHeaderView, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QToolButton, QSplitter, QTableView, QStyledItemDelegate)
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem, QFontMetrics, QFont
from PySide6.QtCore import Qt, QSize, Slot

from .progress_indicator import QProgressIndicator


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

    def __init__(self, side: str, model: str):
        super().__init__()
        self.fetcher_thread = None
        self._init_ui(side, model)
        self._init_connections()

    def _init_ui(self, side: str, model: str):
        self.spinner = self._create_spinner()
        self.consoleWidget = ConsoleWidget()
        self.tableWidget = BaseTable(self.COLUMNS)

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


class BaseTableModel(QStandardItemModel):
    def __init__(self, columns):
        super().__init__()
        self.columns = columns
        self._init_headers()

    def _init_headers(self):
        # 修改表头标签处理逻辑
        self.setHorizontalHeaderLabels([
            item['index'].removesuffix('.rw') if isinstance(item, dict) else item.removesuffix('.rw')
            for item in self.columns
        ])

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        # 检查列是否可编辑
        # column_info = self.columns[index.column()]
        # if isinstance(column_info, dict) and column_info.get('editable', False):
        #     return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class BaseTable(QTableView):
    def __init__(self, columns):
        super().__init__()
        # 移除第一列后的列定义
        self.columns = columns[1:]
        self.model = BaseTableModel(self.columns)
        self._init_table()
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
                background-color: #D2E3FC;
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

    def _adjust_columns(self, custom_widths=None):
        """调整表格列宽"""
        minimum_width = 80
        header = self.horizontalHeader()
        font_metrics = QFontMetrics(self.font())
        padding = 25

        for column in range(self.model.columnCount()):
            column_info = self.columns[column]

            # 检查是否有预定义宽度
            if isinstance(column_info, dict) and 'width' in column_info:
                width = column_info['width']
            else:
                # 获取表头文字
                header_text = self.model.headerData(column, Qt.Horizontal)
                if header_text:
                    width = font_metrics.horizontalAdvance(str(header_text)) + padding
                else:
                    width = minimum_width

            header.setSectionResizeMode(column, QHeaderView.Fixed)
            self.setColumnWidth(column, max(width, minimum_width))

    def _init_table(self):
        self.setModel(self.model)
        self._setup_table_properties()
        self._setup_delegates()
        self._setup_selection_handling()

        COLUMN_WIDTHS = {
            self.model.columnCount() - 1: 200   # 操作列
        }
        self._adjust_columns(COLUMN_WIDTHS)

    def _setup_table_properties(self):
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

    def _setup_delegates(self):
        # 为每列设置适当的delegate
        self.setItemDelegateForColumn(len(self.columns) - 1, OperationDelegate(self))

        for col in range(len(self.columns) - 1):
            self.setItemDelegateForColumn(col, LineEditDelegate(self, prop=self.columns[col]))

    def _update_row_data(self, row: int, lane: int, row_data: dict):
        for col, column_info in enumerate(self.columns[0:-1]):
            # 获取值的键名
            value_key = column_info['index'] if isinstance(column_info, dict) else column_info
            value_key = value_key.removesuffix('.rw')

            value = row_data.get(value_key)
            if value is not None:
                # 设置数据值
                self.model.setData(self.model.index(row, col), str(value))
                # 设置居中对齐
                self.model.setData(self.model.index(row, col), Qt.AlignCenter, Qt.TextAlignmentRole)

                # 检查是否需要创建编辑器
                if column_info.get('editable', False):
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

        self._update_row_data(self._find_or_create_row(lane), lane, row_data)

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
                for col in range(self.model.columnCount() - 1):  # 跳过最后一列（操作列）
                    index = self.model.index(row, col)
                    editor = self.indexWidget(index)
                    if editor and isinstance(editor, QLineEdit):
                        delegate = self.itemDelegateForColumn(col)
                        if isinstance(delegate, LineEditDelegate):
                            delegate.update_background(editor, index)

        self.selectionModel().selectionChanged.connect(on_selection_changed)


class LineEditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop: dict = None):
        super().__init__(parent)
        self.prop = prop or {'type': 'int'}  # 默认类型为int

    def _update_editor_state(self, editor, modified=False):
        """更新编辑器的状态和样式"""
        editor.setProperty("modified", modified)
        editor.style().unpolish(editor)
        editor.style().polish(editor)

    def _handle_text_changed(self, editor, index, text):
        index.model().setData(index, text, Qt.DisplayRole)
        self._update_editor_state(editor, modified=True)

    def update_background(self, editor, index):
        """更新编辑器的背景色"""
        view = self.parent()
        bg_color = "#E8F0FE" if view.selectionModel().isSelected(index) else "#FFFFFF"
        editor.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #DADCE0;
                border-radius: 4px;
                background-color: {bg_color};
            }}
            QLineEdit:focus {{
                border: 1px solid #007AFF;
            }}
            QLineEdit[modified="true"] {{
                color: #007AFF;
            }}
            QLineEdit[error="true"] {{
                color: red;
            }}
            QToolTip {{
                background-color: #FFFBE6;
                color: #000000;
                border: 1px solid #E0E0E0;
                padding: 5px;
                border-radius: 4px;
            }}
        """)

    def validate_input(self, editor, index, text, value_type):
        try:
            if not text:  # 允许空值
                self._update_editor_state(editor, modified=True)
                editor.setProperty("error", False)
                self.update_background(editor, index)
                editor.setToolTip("")
                return

            if value_type == 'int':
                int(text)  # 尝试转换为整数
            elif value_type == 'float':
                float(text)  # 尝试转换为浮点数

            # 验证成功，更新状态
            self._update_editor_state(editor, modified=True)
            editor.setProperty("error", False)
            editor.setToolTip("")
            self.update_background(editor, index)
            self._handle_text_changed(editor, index, text)

        except ValueError:
            # 验证失败，显示错误状态
            editor.setProperty("error", True)
            self.update_background(editor, index)
            error_msg = f"Please enter a valid {'integer' if value_type == 'int' else 'number'}"
            editor.setToolTip(error_msg)
            # 强制更新tooltip
            editor.update()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setAlignment(Qt.AlignCenter)
        # 确保启用鼠标追踪
        editor.setMouseTracking(True)

        # 初始设置背景色
        self.update_background(editor, index)

        # 存储index供后续使用
        editor.setProperty("current_index", index)

        # 根据类型设置验证器和处理函数
        value_type = self.prop.get('type', 'int')

        # 使用类的成员方法作为验证函数
        editor.textChanged.connect(lambda text: self.validate_input(editor, index, text, value_type))

        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setText(str(value) if value is not None else "")
        self._update_editor_state(editor, modified=False)


class OperationDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        # 创建容器widget
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # 修改按钮样式和大小策略
        get_btn = QToolButton(widget)
        get_btn.setText("Get")
        get_btn.clicked.connect(lambda: self._handle_get_clicked(index.row()))
        get_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # 创建Set按钮
        set_btn = QToolButton(widget)
        set_btn.setText("Set")
        set_btn.clicked.connect(lambda: self._handle_set_clicked(index.row()))
        set_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # 添加按钮到布局
        layout.addWidget(get_btn, 1)
        layout.addWidget(set_btn, 1)
        layout.addStretch()

        widget.setStyleSheet("""
            QToolButton {
                background-color: lightgrey;
                color: black;
                border: 1px solid grey;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #79CDCD;
            }
            QToolButton:pressed {
                background-color: #4D4D4D;
            }
        """)

        return widget

    def _handle_get_clicked(self, row):
        """处理Get按钮点击事件"""
        view = self.parent()
        model = view.model

        # 选中当前行
        view.selectRow(row)

        # 从垂直表头获取lane值
        lane = int(model.verticalHeaderItem(row).text().replace('lane', ''))
        # 获取BaseFrame实例
        base_frame = self._get_base_frame(view)
        if base_frame:
            base_frame.show_loading_state()
            base_frame.fetcher_thread = base_frame.create_dev_op_thread('get', lane)
            base_frame.fetcher_thread.row_ready.connect(view.update_row)
            base_frame.fetcher_thread.log_message.connect(base_frame.consoleWidget.console.appendPlainText)
            base_frame.fetcher_thread.finished.connect(base_frame._hide_loading_state)
            base_frame.fetcher_thread.start()

    def _handle_set_clicked(self, row):
        """处理Set按钮点击事件"""
        view = self.parent()
        model = view.model

        # 选中当前行
        view.selectRow(row)

        # 收集可编辑列的数据
        row_data = {}
        for col, header in enumerate(model.columns[:-1]):
            if header.get('editable', False):
                value = model.data(model.index(row, col))
                row_data[header.get('index')] = value

        # 从垂直表头获取lane值
        lane = int(model.verticalHeaderItem(row).text().replace('lane', ''))

        # 获取BaseFrame实例
        base_frame = self._get_base_frame(view)
        if base_frame:
            base_frame.show_loading_state()
            base_frame.fetcher_thread = base_frame.create_dev_op_thread('set', lane, row_data)
            base_frame.fetcher_thread.row_ready.connect(view.update_row)
            base_frame.fetcher_thread.log_message.connect(base_frame.consoleWidget.console.appendPlainText)
            base_frame.fetcher_thread.finished.connect(base_frame._hide_loading_state)
            base_frame.fetcher_thread.start()

    def _get_base_frame(self, widget):
        """获取BaseFrame实例的辅助方法"""
        parent = widget.parent()
        while parent and not isinstance(parent, BaseFrame):
            parent = parent.parent()
        return parent


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
