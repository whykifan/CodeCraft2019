import logging
import sys
import numpy as np
import os
from myRoadTool import MyRoute
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D

'''
code version : 1.0
'''


logging.basicConfig(level=logging.DEBUG,
                    filename='../logs/CodeCraft-2019.log',
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')


class Car:
    def __init__(self, id, start, to, speed, planTime):
        self.id = id
        self.start = start
        self.to = to
        self.speed = speed
        self.planTime = planTime


class Cross:
    def __init__(self, id, road1, road2, road3, road4):
        self.id = id
        self.road = [road1, road2, road3, road4]



class Road:
    def __init__(self, id, length, speed, channel, start, to, isDuplex):
        self.id = id
        self.length = length
        self.speed = speed
        self.channel = channel
        self.start = start
        self.to = to
        self.isDuplex = isDuplex


# to read input file,return car_list cross_list road_list
def data_read(data_path):
    data_list   = []
    with open(data_path,'r') as f:
        for line in f.readlines():
            # 去除首行注释
            if line[0]=='#' :
                continue
            # 去除换行符,括号,并将数据转化为整型
            data_list.append(list(map(int,line.strip('\n').strip('()').split(','))))
        return np.array(data_list)

#change list to dictionary
def change_data(cardata,crossdata,roaddata):
    carDic = {}
    crossDic = {}
    roadDic = {}
    for car in cardata:
        carDic[car[0]] = Car(car[0],car[1],car[2],car[3],car[4])
    for cross in crossdata:
        crossDic[cross[0]] = Cross(cross[0],cross[1],cross[2],cross[3],cross[4])
    for road in roaddata:
        roadDic[road[0]] = Road(road[0],road[1],road[2],road[3],road[4],road[5],road[6])
    return carDic,crossDic,roadDic

# to write output file
def write_answer(answer_path,data):
    #(carId,StartTime,RoadId,...)
    with open(answer_path,'a+') as w :
        for carData in data :
            str_data = str(carData).replace('[','(').replace(']',')')+'\n'
            w.write(str_data)

def getSpeedList(cardata):
    # 得到速度列表，大小由高到低
    speedList = []
    for index, car in cardata.items():
        carSpeed = car.speed
        if carSpeed not in speedList:
            speedList.append(carSpeed)
    return sorted(speedList,reverse=True)

#将数据根据时间-速度进行排序，传入参数为列表类型
def sortSpeedStart(carList):
    sortList = []
    timeList = []
    for time in carList[:,4]:
        if time not in timeList:
            timeList.append(time)
    timeList = sorted(timeList)
    print(timeList)
    for time in timeList:
        saveList = []
        for car in carList:
            if car[4] == time:
               saveList.append([car[0],car[3],car[4]])
        saveList = sorted(saveList,key=lambda x:x[1],reverse=True)
        sortList.append(saveList)
    return sortList

def sortStartSpeed(cardata):
    sortList = []
    speedList = getSpeedList(cardata)
    for speed in speedList:
        saveList = []
        for index, car in cardata.items():
            if car.speed == speed:
               saveList.append([car.id,car.speed,car.planTime])
        saveList = sorted(saveList,key=lambda x:x[2])
        sortList.append(saveList)
    return sortList

def sortDistanceSpeed(cardata,FLOYDMAP):
    sortList = []
    speedList = getSpeedList(cardata)
    for speed in speedList:
        saveList = []
        for index, car in cardata.items():
            if car.speed == speed:
                saveList.append([car.id, car.speed,FLOYDMAP[car.start][car.to], car.planTime])
        saveList = sorted(saveList, key=lambda x:x[2])
        sortList.append(saveList)
    return sortList

#floyd加权矩阵
def getFloydMatrix(crossData,roadData):
    length = crossData.__len__()
    map = {fromId:{toId:np.inf for toId in crossData} for fromId in crossData}
    for fromId in crossData:
        for toId in crossData:
            fromCross = crossData[fromId]
            if fromId == toId:
                map[fromId][toId] = 0
            else:
                roads = fromCross.road
                for roadID in roads:
                    if roadID != -1 :
                        fromID = roadData[roadID].start
                        toID = roadData[roadID].to
                        isDuplex = roadData[roadID].isDuplex
                        if fromID==fromId and toID== toId:
                            map[fromId][toId] = roadData[roadID].length
                        elif(fromID==toId and toID == fromId ):
                            if isDuplex:
                                map[fromId][toId] = roadData[roadID].length
    for k in crossData:
        for i in crossData:
            for j in crossData:
                if map[i][j] > map[i][k] + map[k][j]:
                    map[i][j] = map[i][k] + map[k][j]

    return map

def main():
    '''
    主程序流程：
    1、得到每辆车的路径
    2、逻辑处理
    3、存储出发时间，路径
    '''

    if len(sys.argv) != 5:
        logging.info('please input args: car_path, road_path, cross_path, answerPath')
        exit(1)

    # car_path = sys.argv[1]
    # road_path = sys.argv[2]
    # cross_path = sys.argv[3]
    # answer_path = sys.argv[4]

    car_path = './data/map2/car.txt'
    road_path = './data/map2/road.txt'
    cross_path = './data/map2/cross.txt'


    logging.info("car_path is %s" % (car_path))
    logging.info("road_path is %s" % (road_path))
    logging.info("cross_path is %s" % (cross_path))
    logging.info("answer_path is %s" % (answer_path))

    # to read input file
    # process
    # to write output file

    # # 读取数据，以及数据索引
    # carIndex = ['id', 'from', 'to', 'speed', 'planTime']
    # #             (车辆id，始发地，目的地，最高速度，计划出发时间)
    # crossIndex = ['id', 'roadId1', 'roadId2', 'roadId3', 'roadId4']
    # #             (路口id, 道路id, 道路id, 道路id, 道路id)
    # roadIndex = ['id', 'length', 'speed', 'channel', 'from', 'to', 'isDuplex']
    # #             (道路id，道路长度，最高限速，车道数目，起始点id，终点id，是否双向)

    car_data_list = data_read(car_path)
    cross_data_list = data_read(cross_path)
    road_data_list = data_read(road_path)

   
    # 转化为字典格式
    carDic, crossDic, roadDic = change_data(car_data_list, cross_data_list, road_data_list)

    #得到floydmap,可以得出每个点到终点的最短距离
    floydMap = getFloydMatrix(crossDic,roadDic)

    routeSearch = MyRoute(carDic, crossDic, roadDic,floydMap)
    '''pathList={cadId:[roadId1,...],carId:[roadId1,..],...}'''
    pathList = routeSearch.start()

    speedTimeList = np.array(sortStartSpeed(carDic))
    answerList = []
    k = 0
    SETION_TIME = 480
    WaitTime = 0
    flag30 = 0
    flag45 = 0
    #speed:[8 6 4 2]
    for cars in speedTimeList:
        for car in cars:
            startTime = int(np.random.randint(car[2] + k * SETION_TIME, SETION_TIME * (k + 1), size=1))
            roadList = pathList[car[0]]
            roadList.insert(0, startTime)
            roadList.insert(0, car[0])
            answerList.append(roadList)
        k = k + 1
    write_answer(answer_path, answerList)
if __name__ == "__main__":
    main()
   