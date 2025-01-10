from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout
from PySide6.QtGui import QColor, QFontMetrics, QPalette
from PySide6.QtCore import Qt
from ..components.switch_button import SwitchButton


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

        # 设置SwitchButton透明背景
        switch_palette = editor.palette()
        switch_palette.setColor(QPalette.Base, Qt.transparent)
        switch_palette.setColor(QPalette.Window, Qt.transparent)
        editor.setPalette(switch_palette)

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

        view = self.parent()
        is_editable = view.check_editable(index.column(), index.row())
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

    def updateBackground(self, editor, index):
        """更新编辑器的背景色"""
        view = self.parent()
        bg_color = QColor("#E8F0FE") if view.selectionModel().isSelected(index) else QColor("#FFFFFF")

        container = editor.parent()
        palette = container.palette()
        palette.setColor(QPalette.Base, bg_color)
        palette.setColor(QPalette.Window, bg_color)
        container.setPalette(palette)

    def setEditorReadOnly(self, editor, readonly):
        """设置编辑器的只读状态"""
        switch_button = editor.findChild(SwitchButton)
        if switch_button:
            switch_button.setEnabled(not readonly)
