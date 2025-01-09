from widgets.utils.device_oper_thread import DeviceOperThread
from .utils.base_frame import BaseFrame


class TableOne(BaseFrame):
    # 类级别常量定义
    COLUMNS = [
        {'index': 'lane', 'type': 'vertical header'},
        {'index': 'driver_mode', 'type': 'select', 'editable': True, 'ui': {
            'enum': [
                {'label': 'Normal', 'value': 1},
                {'label': 'Debug', 'value': 2},
                {'label': 'Test', 'value': 3}
            ]
        }},
        {'index': 'prop_1', 'type': 'checkbox', 'editable': True},
        {'index': 'prop_4'},
        {'index': 'prop_6', 'type': 'str', 'editable': True},
        {'index': 'prop_8', 'type': 'boolean', 'editable': True},
        {'index': 'prop_9'},
        {'index': 'Operation', 'type': 'btn', 'width': 200}
    ]
    LANE_COUNT = 4

    table_properties = {
        'strech': True,
    }

    def __init__(self, side):
        self.side = side
        super().__init__(self.side, 'TableOne', self.table_properties)

    def create_dev_op_thread(self, op='get', lane=None, *args):
        if lane is not None:
            lane_list = [lane]
        else:
            lane_list = range(self.LANE_COUNT)

        return DeviceOperThread(
            f"{op}TableOne",
            self.side,
            lane_list,
            *args
        )
