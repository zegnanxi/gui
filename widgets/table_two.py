from widgets.utils.device_oper_thread import DeviceOperThread
from .utils.base_frame import BaseFrame


class TableTwo(BaseFrame):
    # 类级别常量定义
    COLUMNS_ALL = ["lane", "driver_mode.rw", "prop_1", "prop_2ls.ls.rw", "prop_2hs.hs.rw",
                   "prop_6666666666666666666666663",
                   "prop_4", "prop_5.ls", "prop_6.rw", "prop_777777777777abadafddasfadsfadsfadsf", "prop_8", "prop_9", "prop_10", "prop_11",
                   "prop_12", "Operation"]
    LANE_COUNT = 4

    def __init__(self, side):
        self.side = side
        self.COLUMNS = self._process_fields(self.COLUMNS_ALL, self.side)
        # print(f'self.side:{self.side}, self.COLUMNS:{self.COLUMNS}')
        super().__init__()

    def _create_dev_op_thread(self, op='get', lane=None, *args):
        if lane is not None:
            lane_list = [lane]
        else:
            lane_list = range(self.LANE_COUNT)

        return DeviceOperThread(
            f"{op}Driver",
            self.side,
            lane_list,
            *args
        )
