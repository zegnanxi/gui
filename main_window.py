from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QTabWidget, QTabBar)
from widgets.utils.progress_indicator import QProgressIndicator
from widgets.table_one import TableOne
from widgets.table_two import TableTwo
from widgets.table_three import TableThree
import sys
from PySide6.QtWidgets import QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()

    # def _handle_tab_close(self, index: int):
    #     """处理标签页关闭事件"""
    #     print(f'Tab {index} closed')
    #     self.tables[index].cleanup()

    def setup_ui(self):
        """初始化UI组件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        # self.tab_widget.tabCloseRequested.connect(self._handle_tab_close)

        main_layout.addWidget(self.tab_widget)

        # 创建按钮页（第一个标签页）
        button_page = QWidget()
        button_layout = QHBoxLayout(button_page)

        # 创建按钮
        self.btn1 = QPushButton("功能1")
        self.btn2 = QPushButton("功能2")
        self.btn3 = QPushButton("功能3")
        self.buttons = [self.btn1, self.btn2, self.btn3]

        # 添加按钮到布局
        button_layout.addStretch()
        button_layout.addWidget(self.btn1)
        button_layout.addWidget(self.btn2)
        button_layout.addWidget(self.btn3)
        button_layout.addStretch()

        # 添加按钮页为第一个标签页
        self.tab_widget.addTab(button_page, "主页")

        # 禁用第一个标签页的关闭按钮
        self.tab_widget.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, None)

        # 创建表格页
        self.table_one = TableOne()
        self.table_two = TableTwo('Host Side')
        self.table_three = TableThree('Line Side')
        self.tables = [self.table_one, self.table_two, self.table_three]

        # 创建加载指示器
        self.spinner = QProgressIndicator(self)
        self.spinner.hide()

        # 设置窗口属性
        self.resize(1500, 1000)
        self.setWindowTitle("多功能表格示例")

    def setup_connections(self):
        """设置信号连接"""
        self.btn1.clicked.connect(lambda: self.open_table_tab(0))
        self.btn2.clicked.connect(lambda: self.open_table_tab(1))
        self.btn3.clicked.connect(lambda: self.open_table_tab(2))
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

    def open_table_tab(self, index: int):
        """打开表格标签页"""
        # 检查该表格页是否已经打开
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) == self.tables[index]:
                self.tab_widget.setCurrentIndex(i)
                return

        # 如果未打开，添加新标签页
        tab_title = f"表格 {index + 1}"
        self.tab_widget.addTab(self.tables[index], tab_title)
        tab_index = self.tab_widget.count() - 1
        self.tab_widget.setCurrentIndex(tab_index)

        # # 修改这里，直接调用表格的加载方法
        self.tables[index].load_data()

    def close_tab(self, index: int):
        """关闭标签页"""
        if index == 0:
            return
        self.tab_widget.removeTab(index)

    def resizeEvent(self, event):
        """重写 resizeEvent 以在窗口大小改变时调整 spinner 位置"""
        super().resizeEvent(event)
        if self.spinner and not self.spinner.isHidden():
            self.spinner.move(
                self.width() // 2 - self.spinner.width() // 2,
                self.height() // 2 - self.spinner.height() // 2
            )


def main():
    """程序入口函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
