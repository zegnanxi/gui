import time
import random


class GuiApi:
    @classmethod
    def getDriver(cls, side, lane):
        # 添加1秒延迟
        time.sleep(1)

        values = {}
        values['driver_mode'] = random.randint(1, 3)
        values['prop_1'] = random.randint(0, 1)
        values['prop_2ls'] = random.randint(0, 10)
        values['prop_2hs'] = random.randint(0, 10)
        values['prop_6666666666666666666666663'] = random.randint(8, 15)
        values['prop_4'] = random.randint(0, 2)
        values['prop_5'] = random.randint(0, 10)
        values['prop_6'] = '1,2,3,4,5,6,7,8,9,10'
        values['prop_777777777777abadafddasfadsfadsfadsf'] = random.randint(
            0, 10)
        values['prop_8'] = random.choice([True, False])
        values['prop_9'] = random.choice([True, False])
        values['prop_10'] = random.choice([True, False])
        values['prop_11'] = random.randint(0, 1)
        values['prop_12'] = random.randint(0, 10)
        return True, values

    @classmethod
    def setDriver(cls, side, lane, data):
        # 添加1秒延迟
        time.sleep(1)

        return True, data

    @classmethod
    def getAfe(cls, side, lane, dir):
        # 添加1秒延迟
        time.sleep(1)

        values = {}
        values['afe_mode'] = random.randint(0, 2)
        values['afe_1'] = random.randint(0, 5)
        values['afe_2'] = random.randint(0, 1)
        values['afe_6666666666666666666666663'] = random.randint(8, 15)
        values['afe_4'] = random.randint(10, 20)
        values['afe_5'] = random.randint(0, 3)
        values['afe_6'] = random.randint(0, 2)
        values['afe_77'] = random.randint(0, 2)
        values['afe_8'] = random.randint(0, 2)
        return True, values

    @classmethod
    def setAfe(cls, side, lane, dir, data):
        # 添加1秒延迟
        time.sleep(1)

        return True, data

    @classmethod
    def getTableOne(cls, side, lane):
        # 添加1秒延迟
        time.sleep(1)

        values = {}
        values['driver_mode'] = random.randint(1, 3)
        values['prop_1'] = random.randint(0, 2)
        values['prop_4'] = random.randint(0, 1)
        values['prop_6'] = random.randint(8, 15)
        values['prop_8'] = random.choice([True, False])
        values['prop_9'] = random.randint(0, 3)
        return True, values

    @classmethod
    def setTableOne(cls, side, lane, data):
        # 添加1秒延迟
        time.sleep(1)

        return True, data
