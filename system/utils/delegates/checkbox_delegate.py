from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QCheckBox, QStyle
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

        # checkbox.setStyleSheet("""
        #     QCheckBox::indicator:unchecked:disabled {
        #         background-color: #F0F0F0;
        #         border: 1px solid #D0D0D0;
        #         border-radius: 5px;
        #     }
        # """)

        # 修改数据处理逻辑
        value = index.model().data(index, Qt.UserRole)
        checkbox.setChecked(self._convert_to_bool(value))

        view = self.parent()
        checkbox.setEnabled(view.check_editable(index))

        # if view.check_editable(index):
        checkbox.stateChanged.connect(
            lambda state: index.model().setData(index, state, Qt.UserRole)
        )

        layout.addWidget(checkbox)
        return widget

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.UserRole)
        checkbox = editor.findChild(QCheckBox)
        if checkbox:
            checkbox.setChecked(self._convert_to_bool(value))

    def setEditorReadOnly(self, editor, readonly):
        """设置编辑器的只读状态"""
        checkbox = editor.findChild(QCheckBox)
        if checkbox:
            checkbox.setEnabled(not readonly)

    def paint(self, painter, option, index):
        # 只绘制背景，不绘制数据
        style = option.widget.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter, option.widget)

    def _convert_to_bool(self, value):
        """统一处理数据转换"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        try:
            # 处理字符串类型的值
            if isinstance(value, str):
                value = value.strip()
                if value.lower() in ('true', '1'):
                    return True
                if value.lower() in ('false', '0'):
                    return False
            return bool(int(float(value)))
        except (ValueError, TypeError):
            return False
