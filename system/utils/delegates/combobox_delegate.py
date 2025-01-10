from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QComboBox, QSizePolicy
from PySide6.QtCore import Qt


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop: dict = None):
        super().__init__(parent)
        self.prop = prop or {}
        self.enum_options = self.prop.get('ui', {}).get('enum', [])

    def _get_editor_style(self, is_editable: bool, bg_color: str = "#FFFFFF") -> str:
        """获取编辑器的样式

        Args:
            is_editable: 是否可编辑
            bg_color: 背景颜色

        Returns:
            str: 样式表字符串
        """
        return f"""
            QComboBox {{
                background-color: {bg_color};
                border: {('1px solid #DADCE0') if is_editable else 'none'};
                border-radius: 4px;
                padding: 2px 10px;
            }}
            QComboBox:disabled {{
                background-color: {bg_color};
                border: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url(:/icon/image/icon/down.png);
                width: 12px;
                height: 12px;
            }}
        """

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
        view = self.parent()
        is_editable = view.check_editable(index.column(), index.row())
        self.setEditorReadOnly(combobox, not is_editable)

        # 初始设置背景色
        self.updateBackground(combobox, index)

        if is_editable:
            def on_value_changed():
                # 更新数据
                index.model().setData(
                    index,
                    str(combobox.currentData()),
                    Qt.DisplayRole
                )
                # 触发行编辑状态更新
                view = self.parent()
                view.update_editable_states(index.row())

            combobox.currentIndexChanged.connect(on_value_changed)

        # 设置大小策略以填充整个单元格
        combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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

    def updateBackground(self, editor, index):
        """更新编辑器的背景色"""
        view = self.parent()
        is_editable = editor.isEnabled()
        bg_color = "#E8F0FE" if view.selectionModel().isSelected(index) else "#FFFFFF"
        editor.setStyleSheet(self._get_editor_style(is_editable, bg_color))

    def setEditorReadOnly(self, editor, readonly):
        """设置编辑器的只读状态"""
        editor.setEnabled(not readonly)
        editor.setStyleSheet(self._get_editor_style(not readonly))
