import pandas
import json

class User:
    @classmethod
    def generateMissionList(cls, filename):

        with open(filename) as fp:
            user_list_unwrappered = json.loads(fp.read())
            user_list_wrappered = list(map(lambda user: cls(user['portion'],
                                                            user['latitude'],
                                                            user['longitude'],
                                                            user['starttime'],
                                                            user['credit']), user_list_unwrappered))

            return user_list_wrappered

    def __init__(self, portion, latitude, longitude, starttime, credit):
        self.portion = portion
        self.latitude = latitude
        self.longitude = longitude
        self.starttime = starttime
        self.credit = credit
        self.greed_mission_list = []  ##算法一当中用贪心算出来的任务列表
        self.selected_package = None  ##算法二当中分配到的package



