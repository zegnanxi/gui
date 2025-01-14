from ..utils.device_oper_thread import DeviceOperThread
from ..utils.base_frame import BaseFrame


class TableThree(BaseFrame):
    COLUMNS = [
        {'index': 'lane0', 'type': 'checkbox', 'editable': True},
        {'index': 'lane1', 'type': 'checkbox', 'editable': True},
        {'index': 'lane2', 'type': 'checkbox'},
        {'index': 'lane3', 'type': 'checkbox'},
        {'index': 'Operation', 'type': 'btn', 'width': 200}
    ]

    table_properties = {'strech': True}

    LANE_COUNT = 1

    def __init__(self, side, parent):
        self.side = side
        super().__init__(self.side, 'TableThree', {'strech': True, 'row_select': False, 'spliter_size': [100, 400]})
        self.setParent(parent)
        self.load_data()

    def create_dev_op_thread(self, op='get', lane=None, *args):
        if lane is not None:
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
