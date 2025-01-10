from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt, QSize


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

        view = self.parent()
        checkbox.setEnabled(view.check_editable(index.column(), index.row()))

        if view.check_editable(index.column(), index.row()):
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

    def setEditorReadOnly(self, editor, readonly):
        """设置编辑器的只读状态"""
        checkbox = editor.findChild(QCheckBox)
        if checkbox:
            checkbox.setEnabled(not readonly)
