#!/usr/bin/env python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPainter, QFont, QBrush, QColor, QPen


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


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setGeometry(100, 100, 100, 290)
    window.setWindowTitle("Switch Button Example")
    switch1 = SwitchButton()
    switch2 = SwitchButton()
    layout = QVBoxLayout()
    layout.addWidget(switch1)
    layout.addWidget(switch2)
    window.setCentralWidget(QWidget())
    window.centralWidget().setLayout(layout)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
