from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QTabWidget, QTabBar)
from system.dsp.table_one import TableOne
from system.dsp.table_two import TableTwo
from system.dsp.table_three import TableThree
import sys
# import yaml  # 添加在文件开头的导入部分
# import argparse
import subprocess
import os
import qdarktheme
from qdarktheme.qtpy.QtWidgets import QApplication
# 添加资源文件导入
import resources_rc  # 导入编译后的资源文件


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化表格对象列表为 None
        self.tables = []
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
        tabName = f'table_{index + 1}'
        if tabName in self.tables:
            real_index = self.tables.index(tabName) + 1
            self.tab_widget.setCurrentIndex(real_index)
            return

        if index == 0:
            table = TableOne('Line Side', self)
            self.tables.append(tabName)
        elif index == 1:
            table = TableTwo('Host Side', self)
            self.tables.append(tabName)
        elif index == 2:
            table = TableThree('Line Side', self)
            self.tables.append(tabName)

        # 如果未打开，添加新标签页
        self.tab_widget.addTab(table, tabName)
        tab_index = self.tab_widget.count() - 1
        self.tab_widget.setCurrentIndex(tab_index)

        # # 修改这里，直接调用表格的加载方法
        # self.tables[index].load_data()

    def close_tab(self, index: int):
        """关闭标签页"""
        if index == 0:
            return
        self.tables.pop(index - 1)
        self.tab_widget.removeTab(index)

    def update_rpc_server_addr(self, new_addr: str):
        """更新配置文件中的 RPC 服务器地址"""
        config_path = 'conf/conf.yaml'
        try:
            # 读取文件内容
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 只修改包含 rpc_server_addr 的行
            for i, line in enumerate(lines):
                if 'rpc_server_addr' in line:
                    indent = len(line) - len(line.lstrip())  # 保持原有缩进
                    lines[i] = ' ' * indent + f"rpc_server_addr: '{new_addr}'\n"
                    break

            # 写回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"更新配置文件失败: {str(e)}")

    def execute_bat_file(self, rpc_server: str) -> None:
        """执行对应的批处理文件

        Args:
            rpc_server: RPC服务器地址

        Returns:
            None
        """
        # 获取当前工作目录
        current_dir = os.getcwd()

        # 构建批处理文件的路径
        bat_file = os.path.join(
            current_dir,
            'hw',
            'use_local.bat' if rpc_server.startswith('127.0.0.1') else 'use_rpc.bat'
        )

        try:
            # 使用 subprocess.PIPE 来捕获输出，并设置 stdin 以自动处理 pause 命令
            subprocess.run(
                bat_file,
                shell=True,
                check=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            print(f"执行批处理文件失败: {str(e)}")


def main():
    # # 创建命令行参数解析器
    # parser = argparse.ArgumentParser(description='启动主程序')
    # parser.add_argument('--rpc_server', type=str, required=True,
    #                     help='RPC服务器地址，例如: 127.0.0.1:8080')

    # # 解析命令行参数
    # args = parser.parse_args()
    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    qdarktheme.setup_theme('auto')
    window = MainWindow()

    # 更新RPC服务器地址
    # window.update_rpc_server_addr(args.rpc_server)

    # # 执行批处理文件
    # window.execute_bat_file(args.rpc_server)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
