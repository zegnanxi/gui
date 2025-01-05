from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget,
                             QLineEdit, QFileDialog, QGroupBox, QComboBox,
                             QPlainTextEdit)
from PySide6.QtCore import Qt
import sys
from operation import OperationWorker
from progress_indicator import ProgressIndicator

class MainWindow(QMainWindow):
    work_modes = [
            ("Normal", 1),
            ("Debug", 2),
            ("Test", 3)
        ]

    def __init__(self):
        super().__init__()
        self.init_styles()
        self.init_window()
        self.init_ui()
        self.init_signals()
        self.init_loading_spinner()
        self.worker = None

    def init_window(self):
        self.setWindowTitle("我的应用")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(20)

    def init_ui(self):
        # 创建并添加顶部布局
        top_layout = self.create_top_layout()
        # 创建并添加中间布局
        middle_layout = self.create_middle_layout()
        # 创建并添加底部日志区域
        bottom_layout = self.create_bottom_layout()
        
        # 添加到主布局
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(middle_layout)
        self.main_layout.addLayout(bottom_layout)

    def create_top_layout(self):
        reset_group = self.create_reset_group()
        upgrade_group = self.create_upgrade_group()
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(40)
        top_layout.addWidget(reset_group)
        top_layout.addWidget(upgrade_group)
        return top_layout

    def create_reset_group(self):
        power_reset_btn = QPushButton("POWER\nRESET")
        power_reset_btn.setObjectName("power_reset")
        power_reset_btn.setStyleSheet(self.styles['button'])
        
        chip_reset_btn = QPushButton("CHIP\nRESET")
        chip_reset_btn.setObjectName("chip_reset")
        chip_reset_btn.setStyleSheet(self.styles['button'])
        
        reset_layout = QHBoxLayout()
        reset_layout.setSpacing(20)
        reset_layout.setContentsMargins(20, 20, 20, 20)
        reset_layout.addWidget(power_reset_btn, 0, Qt.AlignCenter)
        reset_layout.addWidget(chip_reset_btn, 0, Qt.AlignCenter)

        reset_group = QGroupBox("")
        reset_group.setLayout(reset_layout)
        reset_group.setFixedWidth(220)
        
        return reset_group

    def create_upgrade_group(self):
        upgrade_btn = QPushButton("UPGRADE")
        upgrade_btn.setObjectName("upgrade")
        upgrade_btn.setStyleSheet(self.styles['square_button'])
        
        self.file_input = QLineEdit()
        self.file_input.setStyleSheet(self.styles['file_input'])
        self.file_input.setReadOnly(True)
        self.file_input.setFixedHeight(40)
        
        file_select_btn = QPushButton("File")
        file_select_btn.setObjectName("file_select")
        file_select_btn.setStyleSheet(self.styles['file_button'])
        file_select_btn.setFixedHeight(40)
        
        file_select_layout = QHBoxLayout()
        file_select_layout.setSpacing(0)
        file_select_layout.setContentsMargins(0, 0, 0, 0)
        file_select_layout.addWidget(self.file_input)
        file_select_layout.addWidget(file_select_btn)
        
        upgrade_layout = QHBoxLayout()
        upgrade_layout.setSpacing(20)
        upgrade_layout.setContentsMargins(20, 20, 20, 20)
        upgrade_layout.addWidget(upgrade_btn)
        upgrade_layout.addLayout(file_select_layout)

        upgrade_group = QGroupBox("")
        upgrade_group.setLayout(upgrade_layout)
        upgrade_group.setFixedWidth(480)
        
        return upgrade_group

    def create_middle_layout(self):
        dump_group = self.create_dump_group()
        workmode_group = self.create_workmode_group()
        
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(40)        
        middle_layout.addWidget(dump_group)
        middle_layout.addWidget(workmode_group)
        return middle_layout

    def create_dump_group(self):
        null_button = QPushButton("")
        null_button.setStyleSheet(self.styles['square_button'])
        dump_log = QPushButton("DUMP\nLOG")
        dump_log.setObjectName("dump_log")
        dump_log.setStyleSheet(self.styles['square_button'])

        dump_layout = QHBoxLayout()
        dump_layout.setSpacing(20)
        dump_layout.setContentsMargins(20, 20, 20, 20)
        dump_layout.addWidget(null_button, 0, Qt.AlignCenter)
        dump_layout.addWidget(dump_log, 0, Qt.AlignCenter)

        dump_group = QGroupBox("")
        dump_group.setLayout(dump_layout)
        dump_group.setFixedWidth(220)
        return dump_group

    def create_workmode_group(self):
        workmode_btn = QPushButton("WORK\nMODE")
        workmode_btn.setObjectName("work_mode")
        workmode_btn.setStyleSheet(self.styles['square_button'])
        
        self.mode_select = QComboBox()
        self.mode_select.addItems([mode[0] for mode in self.work_modes])
        self.mode_select.setStyleSheet(self.styles['combobox'])
        self.mode_select.setFixedHeight(40)
        self.mode_select.setCurrentIndex(1)
                                   
        workmode_select_layout = QHBoxLayout()
        workmode_select_layout.setSpacing(0)
        workmode_select_layout.setContentsMargins(0, 0, 0, 0)
        workmode_select_layout.addWidget(self.mode_select)
        
        workmode_layout = QHBoxLayout()
        workmode_layout.setSpacing(20)
        workmode_layout.setContentsMargins(20, 20, 20, 20)
        workmode_layout.addWidget(workmode_btn)
        workmode_layout.addLayout(workmode_select_layout)

        workmode_group = QGroupBox("")
        workmode_group.setLayout(workmode_layout)
        workmode_group.setFixedWidth(480)
        return workmode_group

    def create_bottom_layout(self):
        bottom_layout = QVBoxLayout()
        
        # 创建日志输出框
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(self.styles['log_output'])
        self.log_output.setMinimumHeight(200)
        
        bottom_layout.addWidget(self.log_output)
        return bottom_layout

    def log_message(self, message):
        """添加日志消息到输出框"""
        self.log_output.appendPlainText(message)
        # 滚动到底部
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def init_signals(self):
        # 连接所有信号
        self.findChild(QPushButton, "power_reset").clicked.connect(
            lambda: self.start_operation("power_reset"))
        self.findChild(QPushButton, "chip_reset").clicked.connect(
            lambda: self.start_operation("chip_reset"))
        self.findChild(QPushButton, "upgrade").clicked.connect(
            lambda: self.start_operation("upgrade", file_path=self.file_input.text()))
        self.findChild(QPushButton, "dump_log").clicked.connect(
            lambda: self.start_operation("dump_log"))
        self.findChild(QPushButton, "work_mode").clicked.connect(
            lambda: self.start_operation("work_mode", 
                                       mode_label=self.mode_select.currentText(),
                                       mode_value=self.work_modes[self.mode_select.currentIndex()][1]))
        self.findChild(QPushButton, "file_select").clicked.connect(self.select_file)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "所有文件 (*.*)"
        )
        if file_name:
            self.file_input.setText(file_name)

    def init_loading_spinner(self):
        # 创建加载指示器容器
        self.loading_container = QWidget(self)
        self.loading_container.setFixedSize(100, 100)
        # 移除背景色，保持完全透明
        self.loading_container.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建进度指示器
        self.progress_indicator = ProgressIndicator(self.loading_container)
        self.progress_indicator.setFixedSize(32, 32)
        self.progress_indicator.move(
            (self.loading_container.width() - self.progress_indicator.width()) // 2,
            (self.loading_container.height() - self.progress_indicator.height()) // 2
        )
        
        # 初始状态为隐藏
        self.loading_container.hide()

    def start_operation(self, operation_type, **kwargs):
        # 禁用所有控件
        self.setEnabled(False)
        
        # 显示加载动画
        self.loading_container.move(
            (self.width() - self.loading_container.width()) // 2,
            (self.height() - self.loading_container.height()) // 2
        )
        self.loading_container.show()
        self.progress_indicator.start()
        
        # 创建并启动工作线程
        self.worker = OperationWorker(operation_type, **kwargs)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.log_message.connect(self.log_message)
        self.worker.start()

    def on_operation_finished(self):
        # 停止加载动画
        self.progress_indicator.stop()
        self.loading_container.hide()
        
        # 启用所有控件
        self.setEnabled(True)
        
        # 清理工作线程
        self.worker = None

    def init_styles(self):
        self.styles = {
            'button': """
                QPushButton {
                    border-radius: 37.499999px;
                    min-width: 60px;
                    min-height: 60px;
                    max-width: 60px;
                    max-height: 60px;
                    padding: 5px;
                    background-color: #f0f0f0;
                    text-align: center;
                    border: 2px solid #808080;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-color: #606060;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                    border-color: #404040;
                }
            """,

            'square_button': """
                QPushButton {
                    min-width: 55px;
                    min-height: 50px;
                    max-width: 55px;
                    max-height: 50px;
                    padding: 5px;
                    background-color: #f0f0f0;
                    text-align: center;
                    border: 2px solid #808080;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-color: #606060;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                    border-color: #404040;
                }
            """,            
            
            'file_input': """
                QLineEdit {
                    border: 1px solid #808080;
                    border-top-left-radius: 4px;
                    border-bottom-left-radius: 4px;
                    padding: 5px;
                    background-color: #f8f8f8;
                    min-height: 28px;
                }
            """,
            
            'file_button': """
                QPushButton {
                    border: 1px solid #808080;
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                    padding: 5px 15px;
                    background-color: #f0f0f0;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """,
            
            'combobox': """
                QComboBox {
                    border: 1px solid #808080;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #f8f8f8;
                    min-height: 28px;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: url(down_arrow.png);
                    width: 12px;
                    height: 12px;
                }
                QComboBox:hover {
                    background-color: #e8e8e8;
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #808080;
                    border-radius: 4px;
                    background-color: #f8f8f8;
                    selection-background-color: #e0e0e0;
                }
                QComboBox QAbstractItemView::item {
                    min-height: 28px;
                    padding: 5px;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #e8e8e8;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #e0e0e0;
                }
            """,
            
            'log_output': """
                QPlainTextEdit {
                    border: 1px solid #808080;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #f8f8f8;
                    font-family: Consolas, Monaco, monospace;
                    font-size: 12px;
                }
            """
        }

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
