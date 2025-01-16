from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QComboBox, QSizePolicy, QStyle
from PySide6.QtCore import Qt


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, prop: dict = None):
        super().__init__(parent)
        self.prop = prop or {}
        self.enum_options = self.prop.get('ui', {}).get('enum', [])

    def createEditor(self, parent, option, index):
        # 创建容器widget和布局
        widget = QWidget(parent)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignCenter)

        # 创建combobox
        combobox = QComboBox(parent)

        # 添加选项
        for item in self.enum_options:
            combobox.addItem(item['label'], item['value'])

        # 设置是否可编辑
        view = self.parent()
        is_editable = view.check_editable(index.column(), index.row())
        combobox.setEnabled(is_editable)

        def on_combo_clicked():
            view.selectRow(index.row())

        combobox.showPopup = lambda: (QComboBox.showPopup(combobox), on_combo_clicked())

        if is_editable:
            def on_value_changed():
                index.model().setData(
                    index,
                    combobox.currentData(),
                    Qt.DisplayRole
                )
                view.update_one_line_editable_states(index.row(), index.column())

            combobox.currentIndexChanged.connect(on_value_changed)

        # 修改大小策略和样式
        combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 将combobox添加到布局中
        layout.addWidget(combobox)
        return widget

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        combobox = editor.findChild(QComboBox)
        if combobox:
            try:
                for i in range(combobox.count()):
                    item_value = combobox.itemData(i)
                    if isinstance(item_value, int) and item_value == value:
                        combobox.setCurrentIndex(i)
                        break
                    elif item_value == value:
                        combobox.setCurrentIndex(i)
                        break
            except (ValueError, TypeError):
                combobox.setCurrentIndex(0)

    def setEditorReadOnly(self, editor, readonly):
        """设置编辑器的只读状态"""
        combobox = editor.findChild(QComboBox)
        if combobox:
            combobox.setEnabled(not readonly)

    def paint(self, painter, option, index):
        # 只绘制背景
        style = option.widget.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter, option.widget)
