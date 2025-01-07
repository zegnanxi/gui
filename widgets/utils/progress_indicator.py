from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QTimer, QRect


class QProgressIndicator(QWidget):
    """苹果风格的旋转等待动画控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.setInterval(50)

        self.setFixedSize(32, 32)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 修改窗口标志，添加 Qt.WindowTransparentForInput 使窗口完全透明
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Tool | Qt.WindowTransparentForInput)
        self.setStyleSheet("")  # 移除样式表，使用默认透明背景

    def paintEvent(self, event):
        painter = QPainter(self)
        # 添加 SmoothPixmapTransform 以获得更好的渲染效果
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 确保背景透明
        painter.fillRect(self.rect(), Qt.transparent)

        # 计算中心点和半径
        size = min(self.width(), self.height())
        center = QRect(0, 0, size, size).center()
        radius = size // 3

        # 绘制12个点
        painter.translate(center)
        painter.rotate(self.angle)

        for i in range(12):
            # 计算不透明度
            opacity = (i + 1) / 12
            # color = QColor(0, 0, 0, int(255 * opacity))
            color = QColor(70, 70, 70, int(255 * opacity))  # 使用深灰色
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)

            # 绘制点
            painter.save()
            painter.rotate(i * 30)
            painter.drawEllipse(radius, -2, 4, 4)
            painter.restore()

    def rotate(self):
        """更新旋转角度并重绘"""
        self.angle = (self.angle + 30) % 360
        self.update()

    def start(self):
        """开始动画"""
        self.show()
        self.timer.start()

    def stop(self):
        """停止动画"""
        self.timer.stop()
        self.hide()
