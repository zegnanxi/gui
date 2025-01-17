from ..utils.device_oper_thread import DeviceOperThread
from ..utils.base_frame import BaseFrame


class TableTwo(BaseFrame):
    COLUMNS_ALL = [
        {'index': 'lane', 'type': 'vertical header'},
        {'index': 'driver_mode', 'type': 'select', 'editable': True, 'ui': {
            'enum': [
                {'label': 'Normal', 'value': 1},
                {'label': 'Debug', 'value': 2},
                {'label': 'Test', 'value': 3}
            ]
        }},
        {'index': 'prop_1', 'type': 'checkbox', 'editable': {'driver_mode': [1]}},
        {'index': 'prop_2ls', 'editable': True, 'side': 'Line Side'},
        {'index': 'prop_2hs', 'type': 'select', 'width': 100, 'editable': {'driver_mode': [1]}, 'side': 'Host Side', 'ui': {
            'enum': [
                {'label': 'prop2-1', 'value': 1},
                {'label': 'prop2-2', 'value': 2},
                {'label': 'prop2-3', 'value': 3}
            ]
        }},
        {'index': 'prop_6666666666666666666666663', 'editable': True},
        {'index': 'prop_4', 'type': 'checkbox'},
        {'index': 'prop_5', 'side': 'Line Side'},
        {'index': 'prop_6', 'type': 'str', 'editable': True},
        {'index': 'prop_777777777777abadafddasfadsfadsfadsf'},
        {'index': 'prop_8', 'type': 'boolean', 'width': 120, 'ui': {
            'checked': 'Enabled', 'unChecked': 'Disabled'}, 'editable': True},
        {'index': 'prop_9', 'type': 'boolean', 'width': 100, 'ui': {
            'checked': 'ON', 'unChecked': 'OFF'}},
        {'index': 'prop_10', 'type': 'boolean', 'width': 100, 'editable': True},
        {'index': 'prop_11'},
        {'index': 'prop_12', 'type': 'float'},
        {'index': 'Operation', 'type': 'btn', 'width': 200, 'buttons': ['get', 'set']}
    ]

    LANE_COUNT = 4

    def __init__(self, side, parent):
        self.side = side
        self.COLUMNS = self._process_columns(self.COLUMNS_ALL, self.side)
        super().__init__(self.side, 'Driver', {'horizontal': True})
        self.setParent(parent)
        self.load_data()

    def create_dev_op_thread(self, op='get', lane=None, *args):
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
