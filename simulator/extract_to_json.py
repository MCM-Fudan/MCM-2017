import pandas
import json
import datetime, time

with open("old_missions.json", "w") as fp:
    pf = pandas.read_csv("old_missions.csv")

    empty_dic = list(map(lambda index: {"longitude": float(pf['longitude'][index]),
                                   "latitude": float(pf['latitude'][index]),
                                   "price": float(pf['price'][index]),
                                   "success": int(pf['success'][index])}, pf.index))

    fp.write(json.dumps(empty_dic))



with open("users.json", "w") as fp:
    pf = pandas.read_csv("users.csv")

    pf = pandas.read_csv("users.csv")

    empty_dic = list(map(lambda index: {"longitude": float(pf['longitude'][index]),
                                        "latitude": float(pf['latitude'][index]),
                                        "starttime": pf['starttime'][index][0:-3],
                                        "credit": int(pf['credit'][index]),
                                        "portion": int(pf['portion'][index])}, pf.index))

    fp.write(json.dumps(empty_dic))


with open("new_missions.json", "w") as fp:
    pf = pandas.read_excel('new_mission.xls')

    empty_dic = list(map(lambda index: {"longitude": float(pf['任务GPS经度'][index]),
                                        "latitude": float(pf['任务GPS纬度'][index])}, pf.index))

    fp.write(json.dumps(empty_dic))


