# import user
# import mission
# from user import User
# from mission import Mission
from geopy.distance import vincenty
import json

import pandas

import folium


class DrawMap:
    def __init__(self, latitude, longitude, zoom_start, userFilename, missionFilename):
        self.location = [latitude, longitude]
        self.zoom_start = zoom_start
        self.m = folium.Map(
            location=[latitude, longitude],
            zoom_start=zoom_start
        )
        self.userFilename = userFilename
        self.missionFilename = missionFilename
        self.colormap = {
            "0": "red",
            "1": "green"
        }

    def addUserToMap(self):
        df = pandas.read_excel(self.userFilename)

        for i in df.index:
            try:
                location_str = df['会员位置(GPS)'][i]
                location = list(map(float, location_str.split(" ")))

                credit = int(df['信誉值'][i])

                folium.features.Circle(
                    radius=credit**0.,
                    location=location,
                    popup='Member',
                    color='blue',
                    fill=False,
                ).add_to(self.m)


            except Exception as e:
                print (e)

    def addMissionToMap(self):
        df = pandas.read_excel(self.missionFilename)

        for i in df.index:
            # try:
            color = self.colormap[str(df['任务执行情况'][i])]
            location = list(map(float, [df['任务gps纬度'][i], df['任务gps经度'][i]]))
            value = (df['任务标价'][i]-64) * 100
            folium.features.Circle(
                radius=value,
                location=location,
                popup='Mission',
                color=color,
                fill=False,
            ).add_to(self.m)

            # except Exception as e:
            #     print(e)
    def drawOldMissionDistribution(self):
        self.addUserToMap()
        self.addMissionToMap()

        self.m.save('map2.html')

    def drawPackageDistribution(self):
        


    def drawMap(self):
        self.drawPackageDistribution()
        self.drawOldMissionDistribution()



if __name__ == '__main__':
    drawMap = DrawMap(22.5, 113.9, 10, 'user.xlsx', 'old_mission.xls')
    drawMap.drawMap()

def distance(lat1, long1, lat2, long2):

    location1 = (lat1, long1)
    location2 = (lat2, long2)
    return (vincenty(location1, location2).km)

class User:

    @classmethod
    def generateUserList(cls, filename):

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





class OldMission:

    @classmethod
    def generateMissionList(cls, filename):
        with open(filename) as fp:
            mission_list_unwrappered = json.loads(fp.read())
            mission_list_wrappered = list(map(lambda mission: cls(latitude=mission['latitude'],
                                                                  longitude=mission['longitude'],
                                                                  success=mission['success'],
                                                                  price=mission['price']), mission_list_unwrappered))




            return mission_list_wrappered

    def __init__(self, latitude, longitude, price, success):

        self.latitude = latitude
        self.longitude = longitude
        self.packaged = False  ##当前任务是否已经被打包
        self.allocated = False  ##当前任务是否已经被分配

        self.price = price  ##真实定价,-1表示未定价格
        self.expected_price = -1    ##预计的价格，初始为未知（-1）


        self.success = success ##当前任务的真实结果
        self.simulate_success = -1    ##模拟是否成功，初始为未知（-1）



class TestMission:
    @classmethod
    def generateMissionList(cls, filename):
        with open(filename) as fp:
            mission_list_unwrappered = json.loads(fp.read())
            mission_list_wrappered = list(map(lambda mission: cls(latitude=mission['latitude'],
                                                                  longitude=mission['longitude']), mission_list_unwrappered))

            return mission_list_wrappered

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.packaged = False  ##当前任务是否已经被打包
        self.allocated = False  ##当前任务是否已经被分配

        self.expected_price = -1  ##预计的价格，初始为未知（-1）

        self.simulate_success = -1  ##模拟是否成功，初始为未知（-1）






class Package:
    radius = 5

    def __init__(self, mission_list):
        self.mission_list = mission_list
        self.size = len(mission_list)
        self.latitude, self.longitude = self.generateLocation()
        self.price = self.generatePrice()

    def generatePrice(self):
        '''
        对打包后的包进行定价（naive：直接加和）
        :return: 价值
        '''
        sum_price = 0
        for mission in self.mission_list:
            sum_price += mission.price

        return sum_price



    def generateLocation(self):
        sum_latitude = 0
        sum_longitude = 0
        for mission in self.mission_list:
            sum_latitude += mission.latitude
            sum_longitude += mission.longitude

        return (sum_latitude/self.size, sum_longitude/self.size)




    @classmethod
    def dividePackageAlogirithm(cls, missionList):
        package_list = []

        for mission_outer in missionList:
            if mission_outer.packaged is True:
                continue
            else:
                mission_cluster = [mission_outer]
                for mission_inner in missionList:
                    if(distance(mission_inner.latitude,mission_inner.longitude,
                            mission_outer.latitude,mission_outer.longitude)) < cls.radius \
                            and mission_inner.packaged is False:
                        mission_inner.packaged = True
                        mission_cluster.append(mission_inner)

            package_list.append(cls(mission_cluster))

        return package_list





class Simulator:

    def __init__(self, oldMissionsFilename, usersFilename, newMissionsFilename):
        self.old_mission_list = OldMission.generateMissionList(oldMissionsFilename)
        self.test_mission_list = TestMission.generateMissionList(newMissionsFilename)
        self.user_list = User.generateUserList(usersFilename)
        print(self.old_mission_list[100].success)
        print(self.user_list[100].portion)
        print(self.test_mission_list[100].latitude)

    def start(self):
        packageList = Package.dividePackageAlogirithm(self.old_mission_list)
        print(len(packageList))




if __name__ == '__main__':

    s = Simulator('old_missions.json', 'users.json', 'new_missions.json')
    s.start()