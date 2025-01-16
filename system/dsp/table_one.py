from ..utils.device_oper_thread import DeviceOperThread
from ..utils.base_frame import BaseFrame


class TableOne(BaseFrame):
    # 类级别常量定义
    COLUMNS = [
        {'index': 'row', 'type': 'vertical header'},
        {'index': 'driver_mode', 'type': 'select', 'editable': True, 'ui': {
            'enum': [
                {'label': 'Normal', 'value': 1},
                {'label': 'Debug', 'value': 2},
                {'label': 'Test', 'value': 3}
            ]
        }},
        {'index': 'prop_4', 'editable': {'driver_mode': [2, 3]}},
        {'index': 'prop_1', 'type': 'checkbox', 'editable': True},
        {'index': 'prop_6', 'type': 'str', 'editable': True},
        {'index': 'prop_8', 'type': 'boolean', 'editable': {'driver_mode': [1]}},
        {'index': 'prop_9'},
        {'index': 'Operation', 'type': 'btn', 'width': 200}
    ]
    LANE_COUNT = 8

    def __init__(self, side, parent):
        self.side = side
        super().__init__(self.side, 'TableOne', {'strech': True, 'horizontal': False})
        self.setParent(parent)
        self.load_data()

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
