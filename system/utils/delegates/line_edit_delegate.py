from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit
from PySide6.QtCore import Qt


class LineEditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop: dict = None):
        super().__init__(parent)
        self.prop = prop or {'type': 'int'}

    def _get_editor_style(self, is_editable: bool, bg_color: str = "#FFFFFF") -> str:
        """获取编辑器的样式

        Args:
            is_editable: 是否可编辑
            bg_color: 背景颜色

        Returns:
            str: 样式表字符串
        """
        return f"""
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
        """

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setAlignment(Qt.AlignCenter)
        editor.setMouseTracking(True)

        # 检查是否可编辑
        view = self.parent()
        self.setEditorReadOnly(editor, not view.check_editable(index))

        # 初始设置背景色
        self.updateBackground(editor, index)

        # 存储index供后续使用
        editor.setProperty("current_index", index)

        value_type = self.prop.get('type', 'int')
        editor.textChanged.connect(lambda text: self.validate_input(editor, index, text, value_type))

        return editor

    def setEditorReadOnly(self, editor, readonly):
        """设置编辑器的只读状态"""
        editor.setReadOnly(readonly)
        editor.setStyleSheet(self._get_editor_style(not readonly))

    def updateBackground(self, editor, index):
        """更新编辑器的背景色"""
        view = self.parent()
        is_editable = not editor.isReadOnly()
        bg_color = "#E8F0FE" if view.selectionModel().isSelected(index) else "#FFFFFF"
        editor.setStyleSheet(self._get_editor_style(is_editable, bg_color))

    def validate_input(self, editor, index, text, value_type):
        try:
            if not text:  # 允许空值
                raise ValueError('empty value')

            # 根据类型转换值
            converted_value = None
            if value_type == 'boolean':
                converted_value = bool(text)
            elif value_type == 'float':
                converted_value = float(text)
            elif value_type == 'str':
                converted_value = str(text)
            else:
                converted_value = int(text)

            # 验证成功，更新状态
            self._update_editor_state(editor, modified=True)
            editor.setProperty("error", False)
            editor.setToolTip("")
            self.updateBackground(editor, index)

            # 更新model数据
            index.model().setData(index, converted_value, Qt.UserRole)

        except ValueError:
            # 验证失败，显示错误状态
            editor.setProperty("error", True)
            self.updateBackground(editor, index)
            error_msg = f"Please enter a valid {'integer' if value_type == 'int' else 'number'}"
            editor.setToolTip(error_msg)
            # 强制更新tooltip
            editor.update()

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.UserRole)
        editor.setText(f'{value:.5g}' if isinstance(value, float) else str(value))
        self._update_editor_state(editor, modified=False)

    def _update_editor_state(self, editor, modified=False):
        """更新编辑器的状态和样式"""
        editor.setProperty("modified", modified)
        editor.style().unpolish(editor)
        editor.style().polish(editor)

        # 获取当前index
        current_index = editor.property("current_index")
        if current_index:
            # 更新背景色
            self.updateBackground(editor, current_index)
