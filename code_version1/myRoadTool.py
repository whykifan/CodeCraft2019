import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D

'''
@author:whykifan
@date:2019/3/16
'''

class MyRoute:

    """
    自适应路径搜索
    """
    class Node:
        def __init__(self, currentId, endId,floydMap = None,roadId = None,g=0):
            self.Id = currentId                         # 自己的坐标
            self.father = None                          # 父节点
            self.roadId = roadId                        #用于保存走过road的ID
            self.g = g                                  # g值，g值在用           到的时候会重新算
            #self.h = abs(endId-currentId)              # 计算h值,h值会影响算法的速度，与寻找路线的精度
            if floydMap is not None:
                self.h = floydMap[currentId][endId]
            else:
                self.h = 0
    def __init__(self,carData,crossData,roadData,floydMap):
		#数据类型为字典
        # 开启表
        self.openList = []
        # 关闭表
        self.closeList = []
        #拿到数据
        self.carData = carData
        self.crossData = crossData
        self.roadData = roadData
        self.floydMap = floydMap

    def getMinNode(self):
        """
        获得openlist中F值最小的节点
        :return: Node
        """
        currentNode = self.openList[0]
        #遍历所有节点
        for node in self.openList:
            if node.g + node.h < currentNode.g + currentNode.h:
                currentNode = node
        return currentNode

    def IdInCloseList(self, Id):
        for node in self.closeList:
            if node.Id == Id:
                return True
        return False

    def IdInOpenList(self, Id):
        for node in self.openList:
            if node.Id == Id:
                return node
        return None

    def endIdInCloseList(self,endId):
        for node in self.openList:
            if node.Id == endId:
                return node
        return None

    def searchNear(self, minNode,startId,nextId,endId,roadID):
        """
        搜索代价最小路口
        minNode:代价最小节点
        """
        #设置花费
        spend = self.floydMap[startId][nextId]
        if self.IdInCloseList(nextId):
            return

        #如果不在Openlist，就加入
        currentNode = self.IdInOpenList(nextId)
        if not currentNode:
            currentNode = MyRoute.Node(nextId,endId,floydMap=self.floydMap,roadId=roadID,g = spend)
            currentNode.father = minNode
            self.openList.append(currentNode)
            return

        # 如果在openList中，判断minNode到当前点的G是否更小
        if minNode.g + spend < currentNode.g:  # 如果更小，就重新计算g值，并且改变father
            currentNode.g = minNode.g + spend
            currentNode.father = minNode

    def start(self):
        """
        寻找路径
        :return: roadId列表（路径）
        """
        allRoute = {}
        #字典当中取出一个car
        for id, car in self.carData.items():
            self.openList = []
            # 关闭表
            self.closeList = []
            startId = car.start
            endId = car.to
            # 1.将起点放入openList
            startNode = MyRoute.Node(startId, endId,floydMap=self.floydMap)
            self.openList.append(startNode)
            # 2.主循环逻辑
            while True:
                # 找到F值最小的点
                minNode = self.getMinNode()
                currentId = minNode.Id
                #print(nextId)
                # 把这个点加入closeList中，并且在openList中删除它
                self.closeList.append(minNode)
                self.openList.remove(minNode)
                # 寻找与这个路口相连接的路口
                for roadID in self.crossData[currentId].road:
                    if roadID != -1:
                        fromID = self.roadData[roadID].start
                        toID = self.roadData[roadID].to
                        isDuplex = self.roadData[roadID].isDuplex
                        if isDuplex:
                            if fromID==currentId:
                                self.searchNear(minNode,startId,toID,endId,roadID)
                            else:
                                self.searchNear(minNode,startId,fromID,endId,roadID)
                        else:
                            if fromID==currentId:
                                self.searchNear(minNode,startId,toID,endId,roadID)

                # 判断是否终止
                judgeNode = self.endIdInCloseList(endId)
                if judgeNode:  # 如果终点在关闭表中，就返回结果
                    # print("关闭表中")
                    finalNode = judgeNode
                    pathList = []
                    while True:
                        if finalNode.father:
                            pathList.append(finalNode.roadId)
                            finalNode = finalNode.father
                        else:
                            #pathList.append(car['id'])
                            allRoute[car.id]= list(reversed(pathList))
                            break
                    break
                # if len(self.openList) == 0:
                #     pass
        return allRoute


class dataAnalyse:
    def __init__(self,carDic,roadDic,crossDic):
        self.carDic = carDic
        self.roadDic = roadDic
        self.crossDic = crossDic

    # 车辆启动时间分布
    def showCarStartTime(self):
        cardata = self.carDic
        plt.title('car start time analyse')
        plt.xlabel('planTime')
        plt.ylabel('carNum')
        getTime = []
        for i in range(self.carDic.__len__()):
            if i not in getTime:
                getTime.append(i)
        getTime.sort()
        x = []
        y = []
        for i in getTime:
            j = 0
            for id, car in cardata.items():
                if car.planTime == i:
                    j += 1
            x.append(i)
            y.append(j)
        plt.bar(x, y)
        plt.show()

    # 车辆启动点分布
    def showCarFromId(self):
        cardata = self.carDic
        plt.title('car start cross analyse')
        plt.xlabel('crossId')
        plt.ylabel('carNum')
        x = np.arange(1, 168)
        y = []
        for i in range(1, 168):
            j = 0
            for id, car in cardata.items():
                if car.start == i:
                    j += 1
            y.append(j)
        plt.bar(x, y)
        plt.show()

    # 车辆目的地分布（看起来近似正太分布倒过来）
    def showCarToId(self):
        cardata = self.carDic
        plt.title('car start to analyse')
        plt.xlabel('crossId')
        plt.ylabel('carNum')
        x = np.arange(1, 168)
        y = []
        for i in range(1, 168):
            j = 0
            for id, car in cardata.items():
                if car.to == i:
                    j += 1
            y.append(j)
        plt.bar(x, y)
        plt.show()

    # 每一个时刻出发车辆的速度分布,[8,6,2,4]目前只有四个速度，每个时间数目基本相同
    def showCarSpeed(self):
        cardata = self.carDic
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title('car start time and speed analyse')
        ax.set_xlabel('carStartTime')
        ax.set_ylabel('carSpeed')
        ax.set_zlabel('carNum')

        # 得到速度数据
        speedList = self.getSpeedList()
        print(speedList)
        getTime = []
        for i in range(self.carDic.__len__()):
            if i not in getTime:
                getTime.append(i)
        getTime.sort()
        for planTime in getTime:
            for speed in speedList:
                z = 0
                for id, car in cardata.items():
                    if (car.speed == speed) and (car.planTime == planTime):
                        z += 1
                print(z)
                ax.bar3d(planTime, speed, 0, 1, 1, z)
        plt.show()

    # 车辆到达同一个目的地的车辆启动时间分布,三维柱状图
    def showSameEndSTime(self):
        cardata = self.carDic
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title('car same end start time analyse')
        ax.set_xlabel('carStartTime')
        ax.set_ylabel('toCrossId')
        ax.set_zlabel('carNum')
        getTime = []
        for i in range(self.carDic.__len__()):
            if i not in getTime:
                getTime.append(i)
        getTime.sort()
        for planTime in getTime:
            for crossId in range(1, 168):
                z = 0
                for id, car in cardata.items():
                    if (car.to == crossId) and (car.planTime == planTime):
                        z += 1
                print(z)
                ax.bar3d(planTime, crossId, 0, 1, 1, z)
        plt.show()

    def showCarFromTo(self):
        cardata = self.carDic
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title('car formId and toId analyse')
        ax.set_xlabel('from')
        ax.set_ylabel('to')
        ax.set_zlabel('carNum')
        for start in range(1, 168):
            for to in range(1, 168):
                z = 0
                for id, car in cardata.items():
                    if (car.to == to) and (car.start == start):
                        z += 1
                print(start, to, z)
                ax.bar3d(start, to, 0, 1, 1, z)
        plt.show()

    def getSpeedList(self):
        cardata = self.carDic
        # 得到速度列表，大小由高到低
        speedList = []
        for index, car in cardata.items():
            carSpeed = car.speed
            if carSpeed not in speedList:
                speedList.append(carSpeed)
        return sorted(speedList, reverse=True)

    # 将数据根据时间-速度进行排序，传入参数为列表类型
    def sortPlanTimeStart(self,carList):
        sortList = []
        timeList = []
        for time in carList[:, 4]:
            if time not in timeList:
                timeList.append(time)
        timeList = sorted(timeList)
        print(timeList)
        for time in timeList:
            saveList = []
            for car in carList:
                if car[4] == time:
                    saveList.append([car[0], car[3], car[4]])
            saveList = sorted(saveList, key=lambda x: x[1], reverse=True)
            sortList.append(saveList)
        return sortList

    def sortSpeedPlanTime(self):
        cardata = self.carDic
        sortList = []
        speedList = self.getSpeedList()
        for speed in speedList:
            saveList = []
            for index, car in cardata.items():
                if car.speed == speed:
                    saveList.append([car.id, car.speed, car.planTime])
            saveList = sorted(saveList, key=lambda x: x[2])
            sortList.append(saveList)
        return sortList