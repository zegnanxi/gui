from PySide6.QtWidgets import (
    QHeaderView, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QToolButton, QSplitter, QTableView, QStyledItemDelegate, QCheckBox,
    QComboBox)
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem, QFontMetrics, QFont
from PySide6.QtCore import Qt, QSize, Slot

from .progress_indicator import QProgressIndicator
from .switch_button import SwitchButton


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

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setAlignment(Qt.AlignCenter)
        editor.setMouseTracking(True)

        # 检查是否可编辑
        is_editable = self.prop.get('editable', False)
        editor.setReadOnly(not is_editable)

        # 初始设置背景色
        self.update_background(editor, index)

        # 存储index供后续使用
        editor.setProperty("current_index", index)

        # 只有在可编辑时才添加验证
        if is_editable:
            value_type = self.prop.get('type', 'int')
            editor.textChanged.connect(lambda text: self.validate_input(editor, index, text, value_type))

        # 根据可编辑状态设置不同的样式
        base_style = f"""
            QLineEdit {{
                border: {('1px solid #DADCE0') if is_editable else 'none'};
                border-radius: 4px;
                background-color: #FFFFFF;
            }}
            QLineEdit:focus {{
                border: {('1px solid #007AFF') if is_editable else 'none'};
            }}
            QLineEdit[modified="true"] {{
                color: {'#007AFF' if is_editable else '#000000'};
            }}
            QLineEdit[error="true"] {{
                color: red;
            }}
        """
        editor.setStyleSheet(base_style)

        return editor

    def update_background(self, editor, index):
        """更新编辑器的背景色"""
        view = self.parent()
        is_editable = self.prop.get('editable', False)
        bg_color = "#E8F0FE" if view.selectionModel().isSelected(index) else "#FFFFFF"

        editor.setStyleSheet(f"""
            QLineEdit {{
                border: {('1px solid #DADCE0') if is_editable else 'none'};
                border-radius: 4px;
                background-color: {bg_color};
            }}
            QLineEdit:focus {{
                border: {('1px solid #007AFF') if is_editable else 'none'};
            }}
            QLineEdit[modified="true"] {{
                color: {'#007AFF' if is_editable else '#000000'};
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

        except ValueError:
            # 验证失败，显示错误状态
            editor.setProperty("error", True)
            self.update_background(editor, index)
            error_msg = f"Please enter a valid {'integer' if value_type == 'int' else 'number'}"
            editor.setToolTip(error_msg)
            # 强制更新tooltip
            editor.update()

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setText(str(value) if value is not None else "")
        self._update_editor_state(editor, modified=False)


class SwitchButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop: dict = None):
        super().__init__(parent)
        self.prop = prop or {}  # 存储属性信息

    def createEditor(self, parent, option, index):
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 从prop中获取UI配置
        ui_config = self.prop.get('ui', {})
        editor = SwitchButton(parent, ui_config=ui_config)

        # 根据单元格高度和文字宽度设置开关按钮大小
        cell_height = self.parent().verticalHeader().defaultSectionSize() - 10  # 留出一些边距
        text_width = max(
            QFontMetrics(editor.font()).horizontalAdvance(ui_config.get('checked', SwitchButton.TEXT_NULL)),
            QFontMetrics(editor.font()).horizontalAdvance(ui_config.get('unChecked', SwitchButton.TEXT_NULL))
        )
        switch_width = text_width + cell_height + 15  # 文字宽度 + 滑块宽度(等于高度) + padding

        editor.setFixedSize(switch_width, cell_height)

        # 创建一个水平布局来居中显示SwitchButton
        innerLayout = QHBoxLayout()
        innerLayout.setContentsMargins(0, 0, 0, 0)
        innerLayout.addStretch()
        innerLayout.addWidget(editor)
        innerLayout.addStretch()

        # 使用主布局来包含innerLayout
        layout.addLayout(innerLayout)

        # 设置初始状态和其他属性
        value = index.model().data(index, Qt.DisplayRole)
        editor.state = value.lower() == 'true' if value else False

        is_editable = self.prop.get('editable', False)
        editor.setEnabled(is_editable)

        if is_editable:
            def on_state_changed(state):
                index.model().setData(index, str(state), Qt.DisplayRole)
                self._update_editor_state(editor, modified=True)

            editor.stateChanged.connect(on_state_changed)

        return widget

    def _update_editor_state(self, editor, modified=False):
        """更新编辑器的状态和样式"""
        # 获取顶层容器widget
        container_widget = editor.parent()
        while not isinstance(container_widget, QWidget) or isinstance(container_widget.parent(), QWidget):
            container_widget = container_widget.parent()

        # 设置修改状态
        container_widget.setProperty("modified", modified)
        container_widget.style().unpolish(container_widget)
        container_widget.style().polish(container_widget)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.state = value.lower() == 'true' if value else False


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
        for col, header in enumerate(view.columns[:-1]):
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

    @ Slot()
    def clearConsoleLog(self):
        self.console.clear()


class CheckboxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop: dict = None):
        super().__init__(parent)
        self.prop = prop or {}

    def createEditor(self, parent, option, index):
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        checkbox = QCheckBox(parent)
        # 设置复选框大小
        checkbox.setMinimumSize(QSize(20, 20))

        # 添加样式
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)

        # 其余代码保持不变
        value = index.model().data(index, Qt.DisplayRole)
        try:
            int_value = int(float(value)) if value else 0
            checkbox.setChecked(int_value != 0)
        except (ValueError, TypeError):
            checkbox.setChecked(False)

        checkbox.setEnabled(self.prop.get('editable', False))

        if self.prop.get('editable', False):
            checkbox.stateChanged.connect(
                lambda state: index.model().setData(index, "1" if state else "0", Qt.DisplayRole)
            )

        layout.addWidget(checkbox)
        return widget

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        checkbox = editor.findChild(QCheckBox)
        if checkbox:
            try:
                int_value = int(float(value)) if value else 0
                checkbox.setChecked(int_value != 0)
            except (ValueError, TypeError):
                checkbox.setChecked(False)


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop: dict = None):
        super().__init__(parent)
        self.prop = prop or {}
        self.enum_options = self.prop.get('ui', {}).get('enum', [])

    def createEditor(self, parent, option, index):
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        combobox = QComboBox(parent)
        # 添加选项
        for item in self.enum_options:
            combobox.addItem(item['label'], item['value'])

        # 设置是否可编辑
        combobox.setEnabled(self.prop.get('editable', False))

        # 设置样式
        combobox.setStyleSheet("""
            QComboBox {
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 2px 10px;
                background-color: white;
            }
            QComboBox:disabled {
                background-color: #F8F9FA;
                border: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            # QComboBox::down-arrow {
            #     image: url(:/icon/image/icon/down.png);
            #     width: 12px;
            #     height: 12px;
            # }
        """)

        # 设置大小策略以填充整个单元格
        combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if self.prop.get('editable', False):
            combobox.currentIndexChanged.connect(
                lambda: index.model().setData(
                    index,
                    str(combobox.currentData()),
                    Qt.DisplayRole
                )
            )

        layout.addWidget(combobox)
        return widget

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        combobox = editor.findChild(QComboBox)
        if combobox:
            try:
                value_int = int(value) if value else None
                # 查找匹配的值并设置
                for i in range(combobox.count()):
                    if combobox.itemData(i) == value_int:
                        combobox.setCurrentIndex(i)
                        break
            except (ValueError, TypeError):
                combobox.setCurrentIndex(0)
