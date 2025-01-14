from PySide6.QtWidgets import (QStyledItemDelegate, QWidget, QHBoxLayout,
                               QToolButton, QSizePolicy)


class OperationDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop=None):
        super().__init__(parent)
        self.prop = prop or {}  # 存储按钮配置

    def createEditor(self, parent, option, index):
        # 创建容器widget
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # 从prop中获取按钮配置
        buttons = self.prop.get('buttons', ['set', 'get'])  # 默认显示get和set按钮

        # 创建配置的按钮
        for btn_type in buttons:
            btn = QToolButton(widget)
            btn.setText(btn_type.capitalize())  # 首字母大写
            if btn_type.lower() == 'get':
                btn.clicked.connect(lambda: self._handle_get_clicked(index.row()))
            elif btn_type.lower() == 'set':
                btn.clicked.connect(lambda: self._handle_set_clicked(index.row()))
            btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            layout.addWidget(btn, 1)

        layout.addStretch()

        # 设置按钮样式
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

    def _get_lane_from_row(self, row):
        """从行数据中获取lane值"""
        view = self.parent()
        model = view.model

        # 获取垂直表头配置
        vertical_header_config = view.vertical_header_config
        if vertical_header_config:
            # 获取表头文本
            header_text = model.verticalHeaderItem(row).text()
            # 移除配置中的index前缀
            prefix = vertical_header_config['index']
            if header_text.startswith(prefix):
                return int(header_text[len(prefix):])

        # 如果没有垂直表头配置，则使用行号作为lane
        return row

    def _handle_get_clicked(self, row):
        """处理Get按钮点击事件"""
        view = self.parent()

        # 选中当前行
        view.selectRow(row)

        # 获取lane值
        lane = self._get_lane_from_row(row)

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
                # 根据列配置进行类型转换
                data_type = header.get('type', 'int')
                try:
                    if data_type == 'boolean':
                        value = bool(value)
                    elif data_type == 'float':
                        value = float(value)
                    else:
                        value = int(value)
                except (ValueError, TypeError):
                    print(f"Unable to convert value '{value}' to type {data_type}")
                    continue

                row_data[header.get('index')] = value

        # 获取lane值
        lane = self._get_lane_from_row(row)

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
        # 在方法内部进行导入以避免循环导入
        from ..base_frame import BaseFrame

        parent = widget.parent()
        while parent and not isinstance(parent, BaseFrame):
            parent = parent.parent()
        return parent
