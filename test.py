import pandas
import math
df = pandas.read_excel('old_mission.xls')
for i in df.index:

    location_a = list(map(float, [str(df['任务gps纬度'][i]), str(df['任务gps经度'][i])]))
    location_b = list(map(float, [str(df['任务gps纬度'][i+1]), str(df['任务gps经度'][i+1])]))
    print (math.sqrt((location_a[0]-location_b[0])**2+(location_a[1]-location_b[1])**2))