from widgets.utils.device_oper_thread import DeviceOperThread
from .utils.base_frame import BaseTable


class TableThree(BaseTable):
    # 类级别常量定义
    COLUMNS = ["", "afe_mode", "afe_1", "afe_2", "afe_6666666666666666666666663", "afe_4",
               "afe_5", "afe_6", "afe_77", "afe_8", "Operation"]
    LANE_COUNT = 4

    def __init__(self, side):
        self.side = side
        super().__init__(self.COLUMNS)

    def _create_dev_op_thread(self, op='get', lane=None, *args):
        if lane:
            lane_list = [lane]
        else:
            lane_list = range(self.LANE_COUNT)

        return DeviceOperThread(
            f"{op}Afe",
            self.side,
            lane_list,
            'tx',
            *args
        )
