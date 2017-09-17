
# -*- coding: utf-8 -*-

import json
import random
from functools import reduce
import csv
import folium
import pandas
from geopy.distance import vincenty

import sys

LOWEST_EXPECTATION = 2


class DrawMap:
    def __init__(self, latitude, longitude, zoom_start):
        self.location = [latitude, longitude]
        self.zoom_start = zoom_start
        self.m = folium.Map(
            location=[latitude, longitude],
            zoom_start=zoom_start
        )
        self.colormap = {
            "0": "red",
            "1": "green",
            "2": "brown",
            "3": "blue",
            "4": "pink",
            "5": "purple",
            "6": "black",
            "7": "gray",
            "8": "tan"
        }

    def addUserToMap(self):
        df = pandas.read_excel(self.userFilename)

        for i in df.index:
            try:
                location_str = df['会员位置(GPS)'][i]
                location = list(map(float, location_str.split(" ")))

                credit = int(df['信誉值'][i])

                folium.features.Circle(
                    radius=credit ** 0.,
                    location=location,
                    popup='Member',
                    color='blue',
                    fill=False,
                ).add_to(self.m)


            except Exception as e:
                print(e)

    def addMissionToMap(self):
        df = pandas.read_excel(self.missionFilename)

        for i in df.index:
            # try:
            color = self.colormap[str(df['任务执行情况'][i])]
            location = list(map(float, [df['任务gps纬度'][i], df['任务gps经度'][i]]))
            value = (df['任务标价'][i] - 64) * 100
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
        '''
        画出已知任务的的分布，存储在
        :return:
        '''
        self.addUserToMap()
        self.addMissionToMap()

        self.m.save('map2.html')

    def drawPackageDistribution(self):
        '''
        画出分包之后的任务分布
        :return:
        '''
        color_list = [
            "red",
            "green",
            "brown",
            "blue",
            "pink",
            "purple",
            "black",
            "gray",
            "tan"
        ]

        for package in self.packageList:
            color = color_list[random.randint(0, 8)]  ##这个包本身的颜色
            folium.features.Circle(
                radius=package.price * 4,
                color=color,
                location=(package.latitude, package.longitude),
                popup='Mission',
                fill=False,
            ).add_to(self.m)

            for mission in package.mission_list:
                folium.features.Circle(
                    radius=100,
                    color=color,
                    location=(mission.latitude, mission.longitude),
                    popup='Mission',
                    fill=False,
                ).add_to(self.m)

        self.m.save('package_distribution.html')


def distance(lat1, long1, lat2, long2):
    location1 = (lat1, long1)
    location2 = (lat2, long2)
    dist = vincenty(location1, location2).km

    ##如果太近的话，按照为0.1km计算，避免错误
    if dist<=1e-3:
        return 0.01

    return vincenty(location1, location2).km


class User:

    def __str__(self):
        return "用户location:{0} {1}, credit:{2}".format(str(self.latitude),str(self.longitude),str(self.credit))


    @classmethod
    def generateUserList(cls, filename, total_missions):

        with open(filename) as fp:
            user_list_unwrappered = json.loads(fp.read())
            # total_portions = reduce(lambda a, b: a['portion'] + b['portion'], user_list_unwrappered)

            total_portions = 0

            for user in user_list_unwrappered:
                total_portions += user['portion']

            user_list_wrappered = list(
                map(lambda user: cls(portion=int((user['portion']) * total_missions / total_portions)+1,  ##至少可以抢两个
                                     latitude=user['latitude'],
                                     longitude=user['longitude'],
                                     starttime=user['starttime'],
                                     credit=user['credit']), user_list_unwrappered))

        return user_list_wrappered

    def __init__(self, portion, latitude, longitude, starttime, credit):
        self.portion = portion
        self.latitude = latitude
        self.longitude = longitude
        self.starttime = starttime
        self.credit = credit
        self.greed_mission_list = []  ##算法一当中用贪心算出来的任务列表
        self.selected_package = None  ##算法二当中分配到的package

    def chooseOneMission(self, latitude, longitude, missionList):
        '''
        贪心算法，总是选择value最大的点
        :param latitude: 当前纬度
        :param longitude: 当前经度
        :return: 选出的任务
        '''

        max_value = 0  ##目前期望的最大值
        select_mission = None  ##被选中的任务

        for mission in missionList:
            if mission.allocated == True:
                continue

            value = self.valueMission(latitude, longitude, mission)


            if max_value < value and value > LOWEST_EXPECTATION:
                # print("value:{0}, 用户:{1}， 任务：{2}".format(value, self, mission))
                max_value = value
                select_mission = mission

                ##选中之后标记
            latitude, longitude = mission.latitude, mission.longitude


        if select_mission != None:
            select_mission.allocated = 1
            print("{0}被选中".format(str(select_mission)))
        else:
            print("{0} 选择终止".format(self))

        return select_mission

    def valuePackage(self, package):
        return package.price/distance(package.latitude, package.longitude, self.latitude, self.longitude)

    def selectOnePackage(self, package_list):
        '''
        贪心算法，找出最优的包
        :param package_list:
        :return:
        '''
        max_value = 0
        select_package = None

        for package in package_list:
            value = self.valuePackage(package)
            if value > LOWEST_EXPECTATION*package.size and value > max_value:
                max_value = value
                select_package = package

        if select_package is None:
            return None


        ##把任务设置为已经分配
        for mission in select_package.mission_list:
            mission.allocated = True

        return select_package


    def completeOnePackage(self, package):
        '''
        完成一个包的内容
        :return:
        '''
        probility = 0.64 * (self.credit ** 0.04)

        ##用随机数模拟执行过程
        if random.random() < probility:
            print("{0}成功".format(package))

            for mission in package.mission_list:
                mission.simulate_success = 1
            return True
        else:
            print("{0}失败".format(package))

            for mission in package.mission_list:
                mission.simulate_success = 0

            return False


    def valueMission(self, latitude, longitude, mission):
        '''
        评估任务的价值
        :param latitude
        :param longitude
        :param mission: 需要评估的任务
        :return: 返回任务的价值
        '''

        dist = distance(latitude, longitude, mission.latitude, mission.longitude)
        credit = self.credit
        price = mission.price
        # print("value of Mission is {0}".format(price / dist))
        return price / dist

    def completeOneMission(self, mission):
        '''
        完成一个任务，成功率和信誉度和距离都有关系
        :param mission:
        :return: 是否完成
        '''

        probility = 0.64 * (self.credit**0.04)

        ##用随机数模拟执行过程
        if random.random() < probility:
            print("{0}成功".format(str(mission)))
            mission.simulate_success = 1
            return True
        else:
            print("{0}失败".format(str(mission)))
            mission.simulate_success = 0
            return False


    def completeMissions(self, missionList):
        '''
        一个会员选择并执行任务
        贪婪算法，先找到第一个满足条件的点，再虚拟到达那个点去找下一个满足条件的点，直到找不到点，或者配额已满
        :return:
        '''
        virtual_latitude = self.latitude
        virtual_longitude = self.longitude
        print("{0} 开始选择任务".format(str(self)))

        actual_portion = 0
        success_portion = 0

        for i in range(0, self.portion):
            ##选择任务，如果目前最优任务也无法满足user的期待，则该user的任务已经完成
            mission = self.chooseOneMission(virtual_latitude, virtual_longitude, missionList)
            if mission is None:
                break

            ##执行任务
            actual_portion += 1

            result = self.completeOneMission(mission)
            if result is True:
                success_portion+=1



        print("{0}成功执行的任务数{1}, 分配到的任务数为{2}, 最大份额数{3}".format(self,str(success_portion),str(actual_portion),self.portion))



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

    def __str__(self):
        return "任务 location:{0} {1} price:{2}".format(self.latitude, self.longitude,self.price)

    def __init__(self, latitude, longitude, price, success):
        self.latitude = latitude
        self.longitude = longitude
        self.packaged = False  ##当前任务是否已经被打包
        self.allocated = False ##当前任务是否已经被分配

        self.price = price  ##真实定价,-1表示未定价格
        self.expected_price = -1  ##预计的价格，初始为未知（-1）

        self.success = success  ##当前任务的真实结果
        self.simulate_success = -1  ##模拟是否成功，初始为未知（-1）


class TestMission:
    @classmethod
    def generateMissionList(cls, filename):
        with open(filename) as fp:
            mission_list_unwrappered = json.loads(fp.read())
            mission_list_wrappered = list(map(lambda mission: cls(latitude=mission['latitude'],
                                                                  longitude=mission['longitude']),
                                              mission_list_unwrappered))

            return mission_list_wrappered

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.packaged = False  ##当前任务是否已经被打包
        self.allocated = False  ##当前任务是否已经被分配

        self.expected_price = -1  ##预计的价格，初始为未知（-1）

        self.simulate_success = -1  ##模拟是否成功，初始为未知（-1）


class Package:
    radius = 3

    def __init__(self, mission_list):
        self.mission_list = mission_list

        self.size = len(mission_list)
        self.latitude, self.longitude = self.generateLocation()
        self.price = self.generatePrice()
        self.allocated = False

    def __str__(self):
        return "包size:{0},price: {1},location:{2} {3}".format(self.size, self.price,
                                                              self.latitude,self.longitude)

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

        return (sum_latitude / self.size, sum_longitude / self.size)

    @classmethod
    def dividePackageAlogirithm(cls, missionList):
        package_list = []

        for mission_outer in missionList:
            if mission_outer.packaged is True:
                continue
            else:
                mission_cluster = [mission_outer]
                for mission_inner in missionList:
                    if (distance(mission_inner.latitude, mission_inner.longitude,
                                 mission_outer.latitude, mission_outer.longitude)) < cls.radius \
                            and mission_inner.packaged is False:
                        mission_inner.packaged = True
                        mission_cluster.append(mission_inner)

            package_list.append(cls(mission_cluster))

        return package_list


class Simulator:
    def __init__(self, mode, oldMissionsFilename, usersFilename, newMissionsFilename):
        self.mode = mode
        self.old_mission_list = OldMission.generateMissionList(oldMissionsFilename)
        self.test_mission_list = TestMission.generateMissionList(newMissionsFilename)

        self.drawMap = DrawMap(latitude=23, longitude=113.4, zoom_start=9)

        self.number_of_missions = len(self.old_mission_list)
        self.user_list = User.generateUserList(usersFilename, self.number_of_missions)

        self.number_of_users = len(self.user_list)

        print("总任务数为{0}，总用户数为{1}", self.number_of_missions, self.number_of_users)

    def checkHasPackage(self):
        '''
        当前是否还有包可以分配
        :return:
        '''
        for package in self.packageList:
            if package.allocated is False:
                return True


    def package_mode(self):
        self.user_list.sort(key=lambda user: (user.starttime, -user.credit))

        self.packageList = Package.dividePackageAlogirithm(self.old_mission_list)

        # self.drawMap.drawPackageDistribution()

        allocated_people = 0  ##已经得到任务的人数

        for user in self.user_list:
            if self.checkHasPackage():
                ret_package = user.selectOnePackage(self.packageList)

                if ret_package is None:
                    continue

                user.completeOnePackage(ret_package)
                allocated_people += 1

            else:
                ###如果任务全部分配，则不再分配任务
                print("没有用完人，就结束")
                break

        print("共用人数{0}".format(allocated_people))

        self.checkResult()



    def greedy_mode(self):
        ##把用户先排序
        self.user_list.sort(key=lambda user: (user.starttime, -user.credit))

        allocated_people = 0  ##已经得到任务的人数

        for user in self.user_list:
            if self.checkHasMission():
                user.completeMissions(self.old_mission_list)
                allocated_people += 1

            else:
                ###如果任务全部分配，则不再分配任务
                break


        print("共用人数{0}".format(allocated_people))

        self.checkResult()

    def checkResult(self):
        '''
        检查任务完成情况
        :return:
        '''
        all_count = 0
        choose_count = 0
        simulate_success_count = 0

        for mission in self.old_mission_list:
            all_count += 1
            if mission.simulate_success != -1:
                choose_count += 1
                if mission.simulate_success == 1:
                    simulate_success_count += 1

        print("总个数:{0}\n选中个数:{1}\n成功个数:{2}".format(all_count, choose_count, simulate_success_count))



        with open("test.csv", "w") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(['latitude', 'longitude', 'success', 'simulate_success', 'price'])
            writer.writerows(list(map(lambda mission:
                                        [mission.latitude,
                                         mission.longitude,
                                         mission.success,
                                         mission.simulate_success if mission.simulate_success==1 else 0,
                                         mission.price], self.old_mission_list)))

    def checkHasMission(self):
        '''
        检查当前是否还有任务需要分配
        :param self:
        :return:
        '''

        for mission in self.old_mission_list:
            if mission.allocated == False:
                return True

        return False

    def start(self):
        ##打包，消除竞争
        if self.mode == "package":
            self.package_mode()

        ##不打包的话使用贪心算法
        if self.mode == "greedy":
            self.greedy_mode()



if __name__ == '__main__':
    # fp = open('log', 'w')
    # sys.stdout = fp
    s = Simulator('greedy', 'old_missions.json', 'users.json', 'new_missions.json')
    s.start()

    # fp.close()
