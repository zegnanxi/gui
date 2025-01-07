from PySide6.QtWidgets import (QTableWidgetItem, QHeaderView,
                               QSizePolicy)
from PySide6.QtCore import Qt
from widgets.utils.base_frame import BaseTable


class TableOne(BaseTable):
    # 类级别常量定义
    COLUMNS = ["编号", "数值"]
    DEFAULT_ROW_COUNT = 5
    COLUMN_WIDTHS = {
        0: 120,  # 编号列
        1: 120   # 数值列
    }

    def __init__(self):
        super().__init__(self.COLUMNS)
        self.table_index = 1

        self._init_table_properties()
        self._init_table_appearance()

    def _init_table_properties(self):
        """初始化表格基本属性"""
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _init_table_appearance(self):
        """初始化表格外观"""
        self.verticalHeader().setVisible(False)

        # 设置表头
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

        # 调整列宽
        self.adjust_columns(self.COLUMN_WIDTHS)

    def update_row(self, row_data):
        """更新表格行数据"""
        row = self.rowCount()
        self.insertRow(row)
        self._update_row_data(row, row_data)

    def _update_row_data(self, row: int, row_data: list):
        """更新行数据内容"""
        for col, data in enumerate(row_data):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, col, item)

    def clear(self):
        """清空表格数据"""
        self.setRowCount(0)
