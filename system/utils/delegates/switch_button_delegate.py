from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout
from PySide6.QtGui import QColor, QFontMetrics, QPalette, QPainter, QFont, QBrush, QPen
from PySide6.QtCore import Qt, QRect, Signal


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


class SwitchButton(QWidget):
    TEXT_NULL = '    '

    # 定义信号
    stateChanged = Signal(bool)

    def __init__(self, parent=None, ui_config=None):
        super(SwitchButton, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.state = False
        self._width = 80
        self._height = 40
        # 添加UI配置
        self.ui_config = ui_config or {'checked': SwitchButton.TEXT_NULL, 'unChecked': SwitchButton.TEXT_NULL}
        self.resize(self._width, self._height)

    def set_size(self, width, height):
        """设置开关按钮的尺寸

        Args:
            width (int): 按钮宽度
            height (int): 按钮高度
        """
        self._width = width
        self._height = height
        self.resize(width, height)
        self.update()

    def get_size(self):
        """获取当前按钮尺寸

        Returns:
            tuple: (width, height)
        """
        return (self._width, self._height)

    def mousePressEvent(self, event):
        '''
        set click event for state change
        '''
        super(SwitchButton, self).mousePressEvent(event)
        self.state = False if self.state else True
        # 发射信号
        self.stateChanged.emit(self.state)
        self.update()

    def paintEvent(self, event):
        '''设置按钮样式'''
        super(SwitchButton, self).paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        font = QFont("Arial")
        font.setPixelSize(self.height()//3)
        painter.setFont(font)

        # 定义颜色
        if self.isEnabled():
            on_bg_color = QColor('#6495ED')  # 苹果风格的绿色
            off_bg_color = QColor('#E9E9EA')  # 浅灰色背景
            handle_color = QColor('#FFFFFF')  # 白色滑块
            text_color = QColor('#FFFFFF' if self.state else '#999999')
        else:
            # 禁用状态使用更浅的颜色
            on_bg_color = QColor('#6495ED').lighter(150)  # 更浅的绿色
            off_bg_color = QColor('#F5F5F5')  # 更浅的灰色
            handle_color = QColor('#E0E0E0')  # 灰色滑块
            text_color = QColor('#CCCCCC')

        # SwitchButton state：ON
        if self.state:
            # 绘制背景
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(on_bg_color))
            painter.drawRoundedRect(0, 0, self.width(), self.height(),
                                    self.height()//2, self.height()//2)

            # 绘制滑块
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(handle_color))
            diff_pix = 3
            rect_x = self.width() - diff_pix - (self.height()-2*diff_pix)
            rect_y = diff_pix
            rect_width = (self.height()-2*diff_pix)
            rect_height = (self.height()-2*diff_pix)
            painter.drawEllipse(rect_x, rect_y, rect_width, rect_height)

            # 调整ON文本位置 - 紧靠滑块左侧
            text_width = self.width() * 0.4
            text_height = self.height() * 0.7
            text_x = self.width() - (self.height()-5*diff_pix) - text_width - diff_pix * 5  # 从滑块左侧开始
            text_y = (self.height() - text_height) / 2
            painter.setPen(QPen(text_color))
            painter.setBrush(Qt.NoBrush)
            painter.drawText(QRect(int(text_x), int(text_y),
                                   int(text_width), int(text_height)),
                             Qt.AlignRight | Qt.AlignVCenter,
                             self.ui_config['checked'])
        # SwitchButton state：OFF
        else:
            # 绘制背景
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(off_bg_color))
            painter.drawRoundedRect(0, 0, self.width(), self.height(),
                                    self.height()//2, self.height()//2)

            # 绘制滑块
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(handle_color))
            diff_pix = 3
            rect_x = diff_pix
            rect_y = diff_pix
            rect_width = (self.height()-2*diff_pix)
            rect_height = (self.height()-2*diff_pix)
            painter.drawEllipse(rect_x, rect_y, rect_width, rect_height)

            # 调整OFF文本位置 - 紧靠滑块右侧
            text_width = self.width() * 0.4
            text_height = self.height() * 0.7
            text_x = (self.height()-5*diff_pix) + diff_pix * 5  # 从滑块右侧开始
            text_y = (self.height() - text_height) / 2
            painter.setPen(QPen(text_color))
            painter.setBrush(Qt.NoBrush)
            painter.drawText(QRect(int(text_x), int(text_y),
                                   int(text_width), int(text_height)),
                             Qt.AlignLeft | Qt.AlignVCenter,
                             self.ui_config['unChecked'])
