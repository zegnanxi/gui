from PySide6.QtCore import QThread, Signal
from api.gui_api import GuiApi


class DeviceOperThread(QThread):
    row_ready = Signal(bool, int, dict)
    # 添加信号用于日志输出
    log_message = Signal(str)

    def __init__(self, command, side=1, lane_list=[], *args):
        super().__init__()

        self.command = command
        self.side = side
        self.lane_list = lane_list
        self.extra_args = args

    def run(self):
        for lane in self.lane_list:
            ret, row_data = self._one_lane_op(lane)
            self.row_ready.emit(ret, lane, row_data)

    def _one_lane_op(self, lane):
        self.log_message.emit(f'begin:{lane}')
        api_method = getattr(GuiApi, self.command)
        ret, values = api_method(self.side, lane, *self.extra_args)
        self.log_message.emit(f'end:{lane}')
        # print(f'ret:{ret}, values:{values}')
        return ret, values
