import matplotlib.pyplot as py
import json

stat_file = open("statistics.json",'r')
try:
    stat_data = json.load(stat_file)
except:
    print("statistics data empty")
    exit()
#set x axis for dates
#set y axis for number of follwers and following
x_axis = list(stat_data.keys())
followers_data = []
following_data = []
#print(stat_data)
for date in list(stat_data.keys()):
    followers_data.append(stat_data[date]["newfollowers"])
    following_data.append(stat_data[date]["newfollowing"])
    #print(stat_data[date]["newfollowers"])

#print(x_axis)
#print(following_data)
#print(followers_data)

py.plot(x_axis,followers_data,label = "followers",marker='o')
py.plot(x_axis,following_data,label = "following",marker='o')

py.show()
