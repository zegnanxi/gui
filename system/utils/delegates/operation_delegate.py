from PySide6.QtWidgets import (QStyledItemDelegate, QWidget, QHBoxLayout, QTableView,
                               QToolButton, QSizePolicy)
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import QModelIndex


class OperationDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop=None, horizontal=True):
        super().__init__(parent)
        self.prop = prop or {}  # 存储按钮配置
        self.horizontal = horizontal

    def createEditor(self, parent, option, index):
        # 创建容器widget
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 从prop中获取按钮配置
        buttons = self.prop.get('buttons', ['set', 'get'])  # 默认显示get和set按钮

        # 创建配置的按钮
        for btn_type in buttons:
            btn = QToolButton(widget)
            btn.setText(btn_type.capitalize())  # 首字母大写
            if btn_type.lower() == 'get':
                btn.clicked.connect(lambda: self._handle_get_clicked(index))
            elif btn_type.lower() == 'set':
                btn.clicked.connect(lambda: self._handle_set_clicked(index))
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

    def _get_lane_from_index(self, index: QModelIndex):
        view: QTableView = self.parent()
        model: QStandardItemModel = view.model

        # 根据方向获取正确的索引
        if self.horizontal:
            pos = index.row()
            header_text = model.verticalHeaderItem(pos).text()
        else:
            pos = index.column()
            header_text = model.horizontalHeaderItem(pos).text()

        if view.vertical_header_config:
            # 移除配置中的index前缀
            prefix = view.vertical_header_config['index']
            if header_text.startswith(prefix):
                return int(header_text[len(prefix):])

        # 如果没有表头配置，则使用索引位置作为lane
        return pos

    def _handle_get_clicked(self, index: QModelIndex):
        """处理Get按钮点击事件"""
        view = self.parent()

        if self.horizontal:
            view.selectRow(index.row())
        else:
            view.selectColumn(index.column())

        # 获取lane值
        lane = self._get_lane_from_index(index)

        # 获取BaseFrame实例
        base_frame = self._get_base_frame(view)
        if base_frame:
            base_frame.show_loading_state()
            base_frame.fetcher_thread = base_frame.create_dev_op_thread('get', lane)
            base_frame.fetcher_thread.row_ready.connect(view.update_row)
            base_frame.fetcher_thread.log_message.connect(base_frame.consoleWidget.console.appendPlainText)
            base_frame.fetcher_thread.finished.connect(base_frame._hide_loading_state)
            base_frame.fetcher_thread.start()

    def _handle_set_clicked(self, index: QModelIndex):
        """处理Set按钮点击事件"""
        view: QTableView = self.parent()
        model: QStandardItemModel = view.model

        row_data = {}
        if self.horizontal:
            view.selectRow(index.row())
            for col, header in enumerate(view.columns[:-1]):
                item_index = model.index(index.row(), col)
                editable = header.get('editable', False)
                if not isinstance(editable, bool):
                    editable = view.check_editable(item_index)

                if editable is True:
                    row_data[header.get('index')] = model.data(item_index)
        else:
            view.selectColumn(index.column())
            for row, header in enumerate(view.columns[:-1]):
                item_index = model.index(row, index.column())
                editable = header.get('editable', False)
                if not isinstance(editable, bool):
                    editable = view.check_editable(item_index)

                if editable is True:
                    row_data[header.get('index')] = model.data(item_index)

        # 获取lane值
        lane = self._get_lane_from_index(index)

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
