from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, Property
from PySide6.QtGui import QPainter, QColor

class ProgressIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 基本属性设置
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.setInterval(100)  # 控制旋转速度
        self._delay = 80  # 控制拖尾效果
        self._displayedWhenStopped = False
        self._color = QColor(0, 0, 0)  # 默认颜色
        
        # 设置推荐大小
        self.setFixedSize(20, 20)
        
        # 设置背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        if not self.isVisible():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.timer.isActive() or self._displayedWhenStopped:
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(self.angle)
            
            painter.setPen(Qt.NoPen)
            
            for i in range(8):  # 8个点
                color = QColor(self._color)
                color.setAlphaF(1.0 - (i / 8.0))
                painter.setBrush(color)
                
                painter.save()
                painter.rotate(i * 45)
                painter.drawEllipse(-2, -10, 4, 4)
                painter.restore()

    def start(self):
        self.angle = 0
        self.timer.start()
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def rotate(self):
        self.angle = (self.angle + 45) % 360
        self.update()

    @Property(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @Property(bool)
    def displayedWhenStopped(self):
        return self._displayedWhenStopped

    @displayedWhenStopped.setter
    def displayedWhenStopped(self, state):
        self._displayedWhenStopped = state
        self.update()

    def sizeHint(self):
        return self.size() 