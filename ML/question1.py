import math
from math import sin, cos, sqrt, atan2, radians
import json
import pandas as pd
import csv
from sklearn import linear_model
import matplotlib.pyplot as plt

class CalculateCircle:
    def __init__(self, missionfilename, userfilename, radius):
        self.radius = radius

        df = pd.read_excel(missionfilename)
        self.missions = list(map(lambda i: {"latitude": float(df['任务gps纬度'][i]), "longitude": float(df['任务gps经度'][i]),
                                            "price": float(df['任务标价'][i]), "success": int(df['任务执行情况'][i])}, df.index))

        df = pd.read_excel(userfilename)
        self.users = list(map(lambda i: {"starttime": str(df['预订任务开始时间'][i]),
                                         "credit": float(df['信誉值'][i]),
                                         "portion": int(df['预订任务限额'][i]),
                                         "latitude": list(map(float, df['会员位置(GPS)'][i].split(" ")))[0],
                                         "longitude": list(map(float, df['会员位置(GPS)'][i].split(" ")))[1]
                                         }, df.index))



    def calculateCosts(self):
        for mission in self.missions:

            result = self.caculateCostForEachMission(mission['latitude'], mission['longitude'], 1)
            mission['cost'] = result

    def caculateCostForEachMission(self, latitude, longitude, layer):
        distance_accumulate = 0
        user_count = 0
        for user in self.users:
            distance = self.getDistance(user['latitude'], user['longitude'], latitude, longitude)
            if distance < self.radius*layer and distance > self.radius*(layer-1):
                user_count += 1
                distance_accumulate += distance

        if layer != 1:
            print("layer is {0}, user count is {1}".format(layer, user_count))
        ##本层没有用户，去下一层搜索
        if user_count == 0:
            return self.caculateCostForEachMission(latitude, longitude, layer+1)

        else:
            avg_distance = distance_accumulate / user_count
            return self.accessProximity(user_count, avg_distance, layer)


    def accessProximity(self, user_count, avg_distance, layer):
        print("{0} {1} {2} {3}".format(layer, user_count, (1.0/user_count)*300, avg_distance))
        return ((1.0/user_count)*300*avg_distance)**(layer)



    def getDistance(self, latitude_1, longitude_1, latitude_2, longitude_2):
        radius = 6371

        dLat = (latitude_2 - latitude_1) * math.pi / 180
        dLng = (longitude_2 - longitude_1) * math.pi / 180

        lat1 = latitude_1 * math.pi / 180
        lat2 = latitude_2 * math.pi / 180

        val = sin(dLat / 2) * sin(dLat / 2) + sin(dLng / 2) * sin(dLng / 2) * cos(lat1) * cos(lat2)
        ang = 2 * atan2(sqrt(val), sqrt(1 - val))
        return radius * ang

    def jsonToCSV(self, jsonObj, csvFileName):
        with open(csvFileName, "w") as fp:
            csvwriter = csv.writer(fp)

            count = 0
            for obj in jsonObj:

                if count == 0:
                    header = obj.keys()
                    csvwriter.writerow(header)
                    count += 1

                csvwriter.writerow(obj.values())

    def saveToCSV(self):
        self.jsonToCSV(self.missions, "old_missions.csv")
        self.jsonToCSV(self.users, "users.csv")

    def drawLinear(self):
        df = pd.read_csv("old_missions.csv")

        cost_list = df['cost'].tolist()
        price_list = df['price'].tolist()

        with open('cost.json', 'w') as fp:
            fp.write(json.dumps(cost_list))

        with open('price.json', 'w') as fp:
            fp.write(json.dumps(price_list))

        cost_list = list(map(lambda i: i if i<1600 else 1600, cost_list))

        plt.scatter(cost_list, price_list)


        plt.show()


    def start(self):
        self.calculateCosts()
        self.saveToCSV()
        self.drawLinear()



if __name__ == '__main__':
    calculteCircle = CalculateCircle(missionfilename="old_missions.xls", userfilename="users.xlsx",
                                     radius=5)

    calculteCircle.start()
