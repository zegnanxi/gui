from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QComboBox, QSizePolicy
from PySide6.QtCore import Qt


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop: dict = None):
        super().__init__(parent)
        self.prop = prop or {}
        self.enum_options = self.prop.get('ui', {}).get('enum', [])

    def _get_editor_style(self, is_editable: bool, bg_color: str = "#FFFFFF") -> str:
        """获取编辑器的样式"""
        return f"""
            QComboBox {{
                border: {('1px solid #DADCE0') if is_editable else 'none'};
                border-radius: 4px;
                padding: 2px 10px;
                background-color: {bg_color};
            }}
            QComboBox:disabled {{
                border: none;
                color: #202124;
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
        self.setEditorReadOnly(widget, not is_editable)

        # 初始设置背景色
        self.updateBackground(widget, index)

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

        # 设置基础样式
        combobox.setStyleSheet(self._get_editor_style(is_editable))

        layout.addWidget(combobox)
        return widget

    def setEditorData(self, editor, index):
        combobox = editor.findChild(QComboBox)
        if not combobox:
            return

        value = index.model().data(index, Qt.DisplayRole)
        try:
            value_int = int(value) if value else None
            # 查找匹配的值并设置
            for i in range(combobox.count()):
                if combobox.itemData(i) == value_int:
                    combobox.setCurrentIndex(i)
                    break
        except (ValueError, TypeError):
            self.combobox.setCurrentIndex(0)

    def updateBackground(self, editor, index):
        combobox = editor.findChild(QComboBox)
        if not combobox:
            return

        view = self.parent()
        is_selected = view.selectionModel().isSelected(index)
        is_editable = view.check_editable(index.column(), index.row())

        # 根据状态设置背景色
        bg_color = "#E8F0FE" if is_selected else ("#F8F9FA" if not is_editable else "#FFFFFF")

        # 应用样式
        combobox.setStyleSheet(self._get_editor_style(is_editable, bg_color))

    def setEditorReadOnly(self, editor, readonly):
        """设置编辑器的只读状态"""
        combobox = editor.findChild(QComboBox)
        if not combobox:
            return

        combobox.setEnabled(not readonly)
