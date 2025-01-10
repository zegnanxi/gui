from ..utils.device_oper_thread import DeviceOperThread
from ..utils.base_frame import BaseFrame


class TableThree(BaseFrame):
    # 类级别常量定义
    COLUMNS = [
        {'index': 'lane', 'type': 'vertical header'},
        {'index': 'afe_mode', 'type': 'select', 'editable': True, 'ui': {
            'enum': [
                {'label': 'Normal', 'value': 1},
                {'label': 'Debug', 'value': 2},
                {'label': 'Test', 'value': 3}
            ]
        }},
        {'index': 'afe_1', 'type': 'checkbox', 'editable': True},
        {'index': 'afe_2'},
        {'index': 'afe_6666666666666666666666663', 'type': 'str', 'editable': True},
        {'index': 'afe_4', 'type': 'boolean', 'editable': True},
        {'index': 'afe_5'},
        {'index': 'Operation', 'type': 'btn', 'width': 100, 'buttons': ['get']}
    ]
    LANE_COUNT = 4

    def __init__(self, side):
        self.side = side
        super().__init__(self.side, 'TableThree')

    def create_dev_op_thread(self, op='get', lane=None, *args):
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
