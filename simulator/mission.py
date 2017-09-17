import json

class OldMission:

    @classmethod
    def generateMissionList(cls, filename):
        with open(filename) as fp:
            mission_list_unwrappered = json.loads(fp.read())
            mission_list_wrappered = list(map(lambda mission: cls(success=mission['success'],
                                                                    latitude=mission['latitude'],
                                                                    longitude=mission['longitude'],
                                                                    price=mission['price']), mission_list_unwrappered))

            return mission_list_wrappered

    def __init__(self, latitude, longitude, price, success):

        self.latitude = latitude
        self.longitude = longitude
        self.allocated = False  ##当前任务是否已经被分配

        self.price = price  ##真实定价,-1表示未定价格
        self.expected_price = -1    ##预计的价格，初始为未知（-1）


        self.success = success ##当前任务的真实结果
        self.simulate_success = -1    ##模拟是否成功，初始为未知（-1）


