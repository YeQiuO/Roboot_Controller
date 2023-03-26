import numpy as np
import sys
import math
import Physics4 as Physics4
import Physics2 as Physics2
#F = open('test.txt','a+')
# 完成初始化标记
flag = False
# 工作台信息
worker_infos = []
# 工作台数量
worker_num = 0

# 机器人信息 0:所处工作台; 1:携带物品类型;2:时间价值系数;3:碰撞系数;4:角速度;5.前进速度;6:方向;7:x坐标;8:y坐标;9:x轴线速度;10:y轴线速度
robot_infos = [
    [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
# 预测任务
predict = [-1, -1, -1, -1]
# 0:任务执行状态 -1:无任务;0:执行采购任务;1:执行销售任务
# 1:采购工作台id
# 2:售卖工作台id
robot_task = [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]
# 当前帧数
time = 0
# 当前金钱
money = 0
# 理论金钱
want_money = 0
# 类型依赖图
depend_graph = [
    [0, 0, 0, 1, 1, 0, 0, 0, 1],
    [0, 0, 0, 1, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 1, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
]
# 节点距离图
distance_graph = np.zeros((50, 50))
# 消费者队列
consumer_list = [[], [], [], [], [], [], []]
# 生产者队列
#producer_list = [[], [], [], [], [], [], []]
# 价值队列
value_producer_list = [[], [], []]
# 在产物品数量记录表
on_producing_record = [0, 0, 0, 0, 0, 0, 0]
# 任务队列
task_list = []
# 专属任务队列
custom_task_list = [[], [], [], []]
# 价值系数
value_factor = [1, 1, 1, 100, 110, 120 , 5000]
# 距离系数
distance_factor = 70
# 距离终点系数
distance_center_factor = 30
# 投资系数(同类型消费工作台中，持有物品越多的被优先送的优先级越高)
invest_factor = 10
# 中心点（离中心点越近权值越大）
center = [25,25]
# 7类工作台队列
priority_list = []
# 有7标记
haveSeven = False
# 7类工作台节点
root_node = None
# 有9标记
haveNine = False
# 下一个接收专属任务的机器人id
custom_robot_id = 0
# 场上完成生产的物品类型数量(未被取走的)
finished_num = [0, 0, 0, 0, 0, 0, 0, 0, 0]
# 切换root的控制权
token = 0
# 物品类型利润表
profit = [3000, 3200, 3400, 7100, 7800, 8300, 29000]

# 分组
producer_group = [
    [4, 5, 6, 7, 8, 11, 13, 16, 17, 18, 19, 20, 0, 1, 12, 3, 21],
    [4, 5, 6, 7, 8, 11, 13, 16, 17, 18, 19, 20, 22, 23, 12, 21, 3]
]
consumer_group = [
    [0, 1, 3, 10, 12],
    [12, 14, 21, 22, 23]
]

def read_util_ok():
    while input() != "OK":
        pass


def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()


# 初始化工作台信息
def initWorkerInfo(line):
    global haveSeven
    global haveNine
    infos = line.split(" ")
    info = [0, 0, 0, 0, 0, 0, 0]
    info[0] = int(infos[0])  # 更新工作台类型
    info[1] = float(infos[1])  # 更新x坐标
    info[2] = float(infos[2])  # 更新y坐标
    info[3] = int(infos[3])  # 更新剩余生产时间
    info[4] = int(infos[4])  # 更新原材料格状态
    info[5] = int(infos[5])  # 更新产品格状态

    worker_infos.append(info)

    if info[0] == 7 and haveSeven == False:
        haveSeven = True

    if info[0] == 9 and haveNine == False:
        haveNine = True



# 初始化工作台信息
def updateWorkerInfo(worker_id, line):
    infos = line.split(" ")
    worker_infos[worker_id][1] = float(infos[1])  # 更新x坐标
    worker_infos[worker_id][2] = float(infos[2])  # 更新y坐标
    worker_infos[worker_id][3] = int(infos[3])  # 更新剩余生产时间
    worker_infos[worker_id][4] = int(infos[4])  # 更新原材料格状态
    worker_infos[worker_id][5] = int(infos[5])  # 更新产品格状态

    worker_infos[worker_id][6] = 0  # 更新产品格状态
    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1] #工作台持有物品情况转二进制表示
    # 遍历依赖关系,更新工作台持有物品的数量
    for j in range(9):
        if depend_graph[j][worker_infos[worker_id][0] - 1] == 1 and holder[j + 1] == '1':
            worker_infos[worker_id][6] = worker_infos[worker_id][6] + 1

    # 统计场上完成生产且未取走的物品数量
    if worker_infos[worker_id][5] == 1:
        finished_num[worker_infos[worker_id][0]-1] = finished_num[worker_infos[worker_id][0]-1] + 1

# 获取机器人信息
def updateRobotInfo(robot_id, line):
    infos = line.split(" ")
    robot_infos[robot_id][0] = int(infos[0])  # 更新所在工作台
    robot_infos[robot_id][1] = int(infos[1])  # 更新携带物品类型
    robot_infos[robot_id][2] = float(infos[2])  # 更新时间价值系数
    robot_infos[robot_id][3] = float(infos[3])  # 更新碰撞价值系数
    robot_infos[robot_id][4] = float(infos[4])  # 更新角速度
    speed = (float(infos[5]) ** 2 + float(infos[6]) ** 2) ** 0.5
    robot_infos[robot_id][5] = speed  # 更新线速度
    robot_infos[robot_id][6] = float(infos[7])  # 更新机器人朝向
    robot_infos[robot_id][7] = float(infos[8])  # 更新x坐标
    robot_infos[robot_id][8] = float(infos[9])  # 更新y坐标

    robot_infos[robot_id][9] = float(infos[5])  # 更新x坐标
    robot_infos[robot_id][10] = float(infos[6])  # 更新y坐标


# 刷新生产者队列
def refreshProducerList():
    for i in range(worker_num):
        if worker_infos[i][5] == 1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
            temp_worker_type = worker_infos[i][0]
            if temp_worker_type == 1 or temp_worker_type == 2 or temp_worker_type == 3:
                value_producer_list[2].append(i)
            elif temp_worker_type == 4 or temp_worker_type == 5 or temp_worker_type == 6:
                value_producer_list[1].append(i)
            elif temp_worker_type == 7:
                value_producer_list[0].append(i)
        # 即将完成生产的工作台的物品也被视为可购买
        if worker_num == 18:
            if worker_infos[i][3] < 15 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
                temp_worker_type = worker_infos[i][0]
                if temp_worker_type == 1 or temp_worker_type == 2 or temp_worker_type == 3:
                    value_producer_list[2].append(i)
                elif temp_worker_type == 4 or temp_worker_type == 5 or temp_worker_type == 6:
                    value_producer_list[1].append(i)
            # elif temp_worker_type == 7:
            #     value_producer_list[0].append(i)

            if worker_infos[i][0] == 7 and  worker_infos[i][3] < 140 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
                value_producer_list[0].append(i)

        #图二参数
        if worker_num == 25:
            if worker_infos[i][3] < 10 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
                temp_worker_type = worker_infos[i][0]
                if temp_worker_type == 1 or temp_worker_type == 2 or temp_worker_type == 3:
                    value_producer_list[2].append(i)
                elif temp_worker_type == 4 or temp_worker_type == 5 or temp_worker_type == 6:
                    value_producer_list[1].append(i)
            if worker_infos[i][3] < 30 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (
            not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
                temp_worker_type = worker_infos[i][0]
                if temp_worker_type == 4:
                    value_producer_list[1].append(i)
            if worker_infos[i][3] < 100 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (
            not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
                temp_worker_type = worker_infos[i][0]
                if temp_worker_type == 5:
                    value_producer_list[1].append(i)
            if worker_infos[i][3] < 180 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (
            not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
                temp_worker_type = worker_infos[i][0]
                if temp_worker_type == 6:
                    value_producer_list[1].append(i)

            if worker_infos[i][0] == 7 and  worker_infos[i][3] < 150 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
                value_producer_list[0].append(i)


def refreshProducerList2():
    for i in range(len(value_producer_list)):
        value_producer_list[i].clear()

    for i in range(worker_num):
        worker_id = i
        worker_type = worker_infos[worker_id][0]

        if not isInCurrentProducerGroup(worker_id):
            continue

        if worker_infos[worker_id][5] == 1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
            if worker_type == 1 or worker_type == 2 or worker_type == 3:
                value_producer_list[2].append(i)
            elif worker_type == 4 or worker_type == 5 or worker_type == 6:
                value_producer_list[1].append(i)
            elif worker_type == 7:
                value_producer_list[0].append(i)
            continue
        # if worker_infos[i][3] < 10 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
        #     temp_worker_type = worker_infos[i][0]
        #     if temp_worker_type == 1 or temp_worker_type == 2 or temp_worker_type == 3:
        #         value_producer_list[2].append(i)
        #     elif temp_worker_type == 4 or temp_worker_type == 5 or temp_worker_type == 6:
        #         value_producer_list[1].append(i)
        if worker_infos[i][3] < 10 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
            temp_worker_type = worker_infos[i][0]
            if temp_worker_type == 4:
                value_producer_list[1].append(i)
        if worker_infos[i][3] < 90 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
            temp_worker_type = worker_infos[i][0]
            if temp_worker_type == 5:
                value_producer_list[1].append(i)
        if worker_infos[i][3] < 130 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
            temp_worker_type = worker_infos[i][0]
            if temp_worker_type == 6:
                value_producer_list[1].append(i)
        if worker_infos[i][0] == 7 and  worker_infos[i][3] < 120 and worker_infos[i][3] > -1 and (not producerIsExistInRobotList(i)) and (not producerIsExistInValueList(i)) and (not producerIsExistInCustomTaskList(i)):
            value_producer_list[0].append(i)

# 刷新生产者队列
def insertToProducerList(worker_id):
    if (not producerIsExistInRobotList(worker_id)) and (not producerIsExistInValueList(worker_id)) and (not producerIsExistInCustomTaskList(worker_id)):
        temp_worker_type = worker_infos[worker_id][0]
        if temp_worker_type == 1 or temp_worker_type == 2 or temp_worker_type == 3:
            value_producer_list[2].append(worker_id)
        elif temp_worker_type == 4 or temp_worker_type == 5 or temp_worker_type == 6:
            value_producer_list[1].append(worker_id)
        elif temp_worker_type == 7:
            value_producer_list[0].append(worker_id)

# 序号为worker_id的工作台是否已经存在于任务序列和执行序列以及生产者队列
def producerIsOk(worker_id):
    # 是否存在于执行序列
    for i in range(4):
        if robot_task[i][0] >= 0 and robot_task[i][1] == worker_id:
            return True
    # 是否已经存在于任务序列
    for i in range(len(task_list)):
        if task_list[i][1] == worker_id:
            return True
    # 是否存在于专属任务序列
    for i in range(4):
        for j in range(len(custom_task_list[i])):
            if custom_task_list[i][j][1] == worker_id:
                return True
    return False

# 判断机器人顺路执行该任务所付出的代价是否在承受范围之内
def canTogether(robot_id,buy_id,sell_id):
    r_x = robot_infos[robot_id][7]# 机器人当前x坐标
    r_y = robot_infos[robot_id][8]# 机器人当前y坐标
    old_distance = 0 # 机器人直接去原采购点需要花费的距离
    new_distance = 0 # 机器人先去新采购点将物品放入新售出点再去原采购点需要花费的距离
    if robot_task[robot_id][0] == 0:
        old_buy_id = robot_task[robot_id][1]# 原采购点id
        old_buy_x = worker_infos[old_buy_id][1]# 原采购点x坐标
        old_buy_y = worker_infos[old_buy_id][2]# 原采购点y坐标
        old_distance = calDistance(r_x, r_y, old_buy_x, old_buy_y)# 计算机器人到原采购点的距离
        distance_r2nb = calDistance(r_x, r_y, worker_infos[buy_id][1], worker_infos[buy_id][2])# 计算机器人到新采购点的距离
        distance_bn2ns = distance_graph[buy_id][sell_id]# 计算从新采购点到新销售点的距离
        distance_ns2ob = distance_graph[sell_id][old_buy_id]# 计算从新销售点到原采购点的距离
        new_distance = distance_r2nb + distance_bn2ns + distance_ns2ob# 计算新路线需要花费的距离
        # 如果新距离不超过原有距离的130%
        if old_distance * 1.5 > new_distance:
            return True
    return False

# 判断机器人顺路执行该任务所付出的代价
def calCost(robot_id,buy_id,sell_id):
    r_x = robot_infos[robot_id][7]# 机器人当前x坐标
    r_y = robot_infos[robot_id][8]# 机器人当前y坐标
    old_distance = 0 # 机器人直接去原采购点需要花费的距离
    new_distance = 0 # 机器人先去新采购点将物品放入新售出点再去原采购点需要花费的距离
    if robot_task[robot_id][0] == 0:
        old_buy_id = robot_task[robot_id][1]# 原采购点id
        old_buy_x = worker_infos[old_buy_id][1]# 原采购点x坐标
        old_buy_y = worker_infos[old_buy_id][2]# 原采购点y坐标
        old_distance = calDistance(r_x, r_y, old_buy_x, old_buy_y)# 计算机器人到原采购点的距离
        distance_r2nb = calDistance(r_x, r_y, worker_infos[buy_id][1], worker_infos[buy_id][2])# 计算机器人到新采购点的距离
        distance_bn2ns = distance_graph[buy_id][sell_id]# 计算从新采购点到新销售点的距离
        distance_ns2ob = distance_graph[sell_id][old_buy_id]# 计算从新销售点到原采购点的距离
        new_distance = distance_r2nb + distance_bn2ns + distance_ns2ob# 计算新路线需要花费的距离
        # 如果新距离不超过原有距离的130%
        return new_distance - old_distance
    return -1

# 检测是否存在顺路的任务
def generateTogetherTask(robot_id):
    # 只在去采购的路上顺路做任务
    if robot_task[robot_id][0] != 0:
        return
    # 遍历消费者列表，找到机器人附近可以顺路做的任务
    for i in range(len(consumer_list)):
        for j in range(len(consumer_list[i])):
            consumer_id = consumer_list[i][j] # 可用的消费者id
            consumer_type = i + 1 #消费者想要的物品类型
            # 当消费点与机器人当前需要执行的采购任务点非常接近时，说明在完成该消费任务后能顺便继续做采购任务，因此尝试为其寻找适合的采购点
            if distance_graph[robot_task[robot_id][1]][consumer_id] < 2:
                # print('%d号机器人3米内有%d号工作台需要%d类型材料' %(robot_id,consumer_id,consumer_type),file=F)
                # 确定消费者需要的物品类型在value_task_list的哪一行可以寻找到
                level = 0
                if consumer_type == 1 or consumer_type == 2 or consumer_type == 3:
                    level = 2
                elif consumer_type == 4 or consumer_type == 5 or consumer_type == 6:
                    level = 1
                elif consumer_type == 7:
                    level = 0
                # 遍历value_task_list目标行寻找适配的采购点
                for k in range(len(value_producer_list[level])):
                    producer_id = value_producer_list[level][k] #可用的采购点id
                    product_type = worker_infos[producer_id][0] #该采购点提供的物品类型
                    # 判断该采购点生成的物品类型是否是消费点需要的类型，同时顺路做该任务的代价必须在承受范围，
                    # 如果符合条件则将这个任务作为机器人当前的任务，原任务在该任务执行完之后再执行(即将原任务放入机器人专属任务队列的首位)
                    if product_type == consumer_type and canTogether(robot_id,producer_id,consumer_id):
                        # print('%d工作点符合条件,可以进行任务切换' % (producer_id),file=F)
                        # print('旧任务为从%d出发运送%d类物品到%d号工作台' % ( robot_task[robot_id][1], worker_infos[robot_task[robot_id][1]][0], robot_task[robot_id][2]), file=F)
                        # print('新任务为从%d出发运送%d类物品到%d号工作台' % (producer_id,product_type,consumer_id),file=F)
                        task = [0,robot_task[robot_id][1],robot_task[robot_id][2]]
                        robot_task[robot_id][0] = 0
                        robot_task[robot_id][1] = producer_id
                        robot_task[robot_id][2] = consumer_id
                        custom_task_list[robot_id].insert(0,task)
                        removeProducerFromValueProducerList(producer_id)
                        removeConsumerFromConsumerList(consumer_id,product_type)
                        return

def robExecutingTask(robot_id):
    if robot_task[robot_id][0] == -1:
        return False
    r_x = robot_infos[robot_id][7]
    r_y = robot_infos[robot_id][8]
    r_buy_id = robot_task[robot_id][1]
    r_sell_id = robot_task[robot_id][2]
    # 执行购买任务前遇到顺路的任务则进行抢断
    for m in range(4):
        # 只抢占其他机器人采购阶段的任务
        if m == robot_id or robot_task[m][0] != 0 or robot_task[robot_id][0] != 0:
            continue
        buy_id = robot_task[m][1]
        sell_id = robot_task[m][2]
        distance_r2p = calDistance(r_x, r_y, worker_infos[buy_id][1],worker_infos[buy_id][2])  # 计算robot_id到该任务采购点的距离
        distance_m2p = calDistance(robot_infos[m][7], robot_infos[m][8], worker_infos[buy_id][1],worker_infos[buy_id][2])  # 计算m到该任务采购点的距
        # 如果m号机器人的采购点在robot_id号机器人附近，且要去的m号机器人采购点的距离小于m号机器人自己去采购点距离的一半，同时能顺路执行，那就抢占该任务
        if distance_r2p < 50 and canTogether(robot_id,buy_id,sell_id) and distance_r2p < distance_m2p/1.8:
            #print('%d号机器人成功抢占%d号机器人的任务,去的采购的路上顺路做' % (robot_id, m), file=F)
            task = [0, robot_task[robot_id][1], robot_task[robot_id][2]]
            robot_task[robot_id][0] = 0
            robot_task[robot_id][1] = buy_id
            robot_task[robot_id][2] = sell_id
            custom_task_list[robot_id].insert(0, task)
            robot_task[m][0] = -1
            return True
    # 遇到其他机器人的买点与自己要去的卖点一致，且其他机器人去该点也较远时，进行任务抢占
    for m in range(4):
        # 只抢占其他机器人采购阶段的任务
        if m == robot_id or robot_task[m][0] != 0:
            continue
        buy_id = robot_task[m][1]
        sell_id = robot_task[m][2]
        distance_r2c = 0
        distance_r2p = calDistance(r_x, r_y, worker_infos[r_buy_id][1], worker_infos[r_buy_id][2])
        distance_p2c = distance_graph[r_buy_id, r_sell_id]
        if robot_task[robot_id][0] == 0:
            distance_r2c = distance_r2p + distance_p2c
        else:
            distance_r2c = calDistance(robot_infos[robot_id][7], robot_infos[robot_id][8],worker_infos[buy_id][1], worker_infos[buy_id][2])
        distance_m2c = calDistance(robot_infos[m][7], robot_infos[m][8], worker_infos[buy_id][1], worker_infos[buy_id][2])
        # 如果m号机器人的采购点在robot_id号机器人附近，且要去的m号机器人采购点的距离小于m号机器人自己去采购点距离的一半，同时能顺路执行，那就抢占该任务
        if buy_id == robot_task[robot_id][2] and distance_m2c > distance_r2c/1 and distance_m2c > 15:
            #print('%d号机器人成功抢占%d号机器人的任务,卖完了之后顺路做' % (robot_id, m), file=F)
            task = [0, buy_id, sell_id]
            custom_task_list[robot_id].insert(0, task)
            robot_task[m][0] = -1
            return True
    # 执行购买任务前遇到顺路的其他机器人的待办任务则进行抢断
    for m in range(4):
        if m == robot_id:
            continue
        for n in range(len(custom_task_list[m])):
            buy_id = custom_task_list[m][n][1]
            sell_id = custom_task_list[m][n][2]
            distance_r2p = calDistance(r_x, r_y, worker_infos[buy_id][1], worker_infos[buy_id][2])  # 计算robot_id到该任务采购点的距离
            distance_m2p = calDistance(robot_infos[m][7], robot_infos[m][8], worker_infos[buy_id][1], worker_infos[buy_id][2])  # 计算m到该任务采购点的距
            # 如果m号机器人的采购点在robot_id号机器人附近，且要去的m号机器人采购点的距离小于m号机器人自己去采购点距离的一半，同时能顺路执行，那就抢占该任务
            if distance_r2p < 50 and canTogether(robot_id,buy_id,sell_id) and distance_r2p < distance_m2p/2:
                #print('%d号机器人成功抢占%d号机器人的后备任务,去的采购的路上顺路做' % (robot_id, m), file=F)
                task = [0, robot_task[robot_id][1], robot_task[robot_id][2]]
                robot_task[robot_id][0] = 0
                robot_task[robot_id][1] = buy_id
                robot_task[robot_id][2] = sell_id
                custom_task_list[robot_id].insert(0, task)
                del custom_task_list[m][n]
                return True
    # 遇到其他机器人后备任务的买点与自己要去的卖点一致，且其他机器人去该点也较远时，进行任务抢占
    for m in range(4):
        if m == robot_id:
            continue
        for n in range(len(custom_task_list[m])):
            buy_id = custom_task_list[m][n][1]#后备任务采购点
            sell_id = custom_task_list[m][n][2]#后备任务售卖点
            distance_r2c = 0# 当前机器人到自身售卖点的距离
            distance_m2c = 0#m号机器人完成自身当前任务所需距离

            if robot_task[m][0] == 0:
                distance_m2p = calDistance(robot_infos[m][7], robot_infos[m][8], worker_infos[robot_task[m][1]][1], worker_infos[robot_task[m][1]][2])
                distance_m2c = distance_m2p + distance_graph[robot_task[m][1]][robot_task[m][2]]
            else:
                distance_m2c = calDistance(robot_infos[m][7], robot_infos[m][8], worker_infos[robot_task[m][2]][1],  worker_infos[robot_task[m][2]][2])

            if robot_task[robot_id][0] == 0:
                distance_r2p = calDistance(r_x, r_y, worker_infos[r_buy_id][1], worker_infos[r_buy_id][2])
                distance_r2c = distance_r2p + distance_graph[r_buy_id][r_sell_id]
            else:
                distance_r2c = calDistance(r_x, r_y, worker_infos[r_sell_id][1], worker_infos[r_sell_id][2])
            if buy_id == robot_task[robot_id][2] and distance_m2c > distance_r2c:
                task = [0, buy_id, sell_id]
                custom_task_list[robot_id].insert(0, task)
                del custom_task_list[m][n]
                return True

    return False

def generateTogetherTask2(robot_id):
    global time
    # 只在去采购的路上顺路做任务
    if robot_task[robot_id][0] != 0:
        return
    # print('%d号机器人尝试获取顺风车任务' % robot_id,file=F)
    if globalIsLoseBalance() and worker_infos[robot_task[robot_id][2]][0] == getMinTypeOf456():
        # print('均衡破坏,无法接顺风任务',file=F)
        return

    # 遍历生产者列表，找到机器人附近可以顺路做的任务
    for i in range(len(value_producer_list)):
        level = 2-i
        for j in range(len(value_producer_list[level])):
            producer_id = value_producer_list[level][j] # 可用的生产者id
            product_type = worker_infos[producer_id][0] #生产的物品类型
            # 当消费点与机器人当前需要执行的采购任务点非常接近时，说明在完成该消费任务后能顺便继续做采购任务，因此尝试为其寻找适合的采购点
            distance_r2p = calDistance(robot_infos[robot_id][7], robot_infos[robot_id][8], worker_infos[producer_id][1], worker_infos[producer_id][2])# 计算机器人到可用生产者的距离
            # 当机器人5米范围内有物品可以送时，判断该物品有没有顺路的消费点，同时付出的代价在阈值之内，选择代价最小的
            if distance_r2p < 20:
                # print('%d号机器人20米内有%d号工作台以及完成%d类型材料的生产' %(robot_id,producer_id,product_type),file=F)
                # 遍历消费者列表找到合适的消费者
                min_cost = 200
                min_consumer_id = -1
                for k in range(len(consumer_list[product_type-1])):
                    consumer_id = consumer_list[product_type-1][k] #可用的消费点id
                    if canTogether(robot_id, producer_id, consumer_id) and calCost(robot_id, producer_id, consumer_id) < min_cost:
                        min_cost = calCost(robot_id, producer_id, consumer_id)
                        min_consumer_id = consumer_id


                if min_consumer_id != -1:
                    # print('%d工作点符合条件,可以进行任务切换' % (producer_id),file=F)
                    # print('旧任务为从%d出发运送%d类物品到%d号工作台' % ( robot_task[robot_id][1], worker_infos[robot_task[robot_id][1]][0], robot_task[robot_id][2]), file=F)
                    # print('新任务为从%d出发运送%d类物品到%d号工作台' % (producer_id,product_type,min_consumer_id),file=F)
                    new_task = [0, producer_id, min_consumer_id]# 顺路任务
                    task = [0, robot_task[robot_id][1], robot_task[robot_id][2]]
                    robot_task[robot_id][0] = 0
                    robot_task[robot_id][1] = new_task[1]
                    robot_task[robot_id][2] = new_task[2]
                    custom_task_list[robot_id].insert(0, task)
                    removeProducerFromValueProducerList(producer_id)
                    removeConsumerFromConsumerList(min_consumer_id, product_type)
                    return

# 判断场上的456是否发生了失衡
def globalIsLoseBalance():
    n4 = on_producing_record[3] + finished_num[3]
    n5 = on_producing_record[4] + finished_num[4]
    n6 = on_producing_record[5] + finished_num[5]
    for i in range(len(priority_list)):
        if isHoldWorkerType(priority_list[i],4):
            n4 = n4 + 1
        if isHoldWorkerType(priority_list[i],5):
            n5 = n5 + 1
        if isHoldWorkerType(priority_list[i],6):
            n6 = n6 + 1

    num = [n4, n5, n6]
    max_n = n4
    min_n = n4
    for i in range(len(num)):
        if num[i] > max_n:
            max_n = num[i]
        if num[i] < min_n:
            min_n = num[i]
    if max_n - min_n >= 1:
        return True
    return False
# 工作台是否集齐原材料准备进入生产
def producerIsReady(worker_id):
    worker_type = worker_infos[worker_id][0]
    if getNeedProductCount(worker_type) == worker_infos[worker_id][6]:
        return True
    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    holder_num = 0
    for i in range(9):
        temp_type = i+1
        if depend_graph[temp_type-1][worker_type - 1] == 1 and holder[temp_type] == '1':
            holder_num += 1
            continue
        if depend_graph[temp_type - 1][worker_type - 1] == 1 and holder[temp_type] == '0':
            for j in range(4):
                if robot_task[j][0] != -1 and robot_task[j][2] == worker_id and worker_infos[robot_task[j][1]][0] == temp_type:
                    holder_num += 1
                    break
            continue
    if holder_num == getNeedProductCount(worker_type):
        return True
    return False

# 获取456中数量最少的类型
def getMinTypeOf456():
    global time
    if not haveSeven:
        return -1
    if time > 8000:
        return -1
    #在产的和完成生产待取走的
    n4 = on_producing_record[3] + finished_num[3]
    n5 = on_producing_record[4] + finished_num[4]
    n6 = on_producing_record[5] + finished_num[5]
    # 在路上的(机器人拿着的)
    for i in range(4):
        if robot_task[i][0] == 1 and worker_infos[robot_task[i][1]][0] == 4:
            n4 = n4 + 1
        if robot_task[i][0] == 1 and worker_infos[robot_task[i][1]][0] == 5:
            n5 = n5 + 1
        if robot_task[i][0] == 1 and worker_infos[robot_task[i][1]][0] == 6:
            n6 = n6 + 1
    # 7手上拿着的
    for i in range(worker_num):
        if worker_infos[i][0] != 7:
            continue
        if isHoldWorkerType(i, 4):
            n4 = n4 + 1
        if isHoldWorkerType(i, 5):
            n5 = n5 + 1
        if isHoldWorkerType(i, 6):
            n6 = n6 + 1
    for i in range(worker_num):
        if producerIsReady(i) and worker_infos[i][0] == 4:
            n4 = n4 + 1
        if producerIsReady(i) and worker_infos[i][0] == 5:
            n5 = n5 + 1
        if producerIsReady(i) and worker_infos[i][0] == 6:
            n6 = n6 + 1

    num = [n4, n5, n6]
    min_type = 4
    max_n = n4
    min_n = n4
    for i in range(len(num)):
        if num[i] > max_n:
            max_n = num[i]
        if num[i] < min_n:
            min_n = num[i]
            min_type = i+4
    # 若最大的与最小的数量相等，则说明当前平衡
    if max_n == min_n:
        min_type = 4
    if min_n > 4:
        return -1
    return min_type

# 消费consume_type类型物品序号为worker_id的工作台是否已经存在于专属任务序列和执行序列以及消费者队列
def consumerIsOk(worker_id, consume_type):
    # 是否存在于消费者队列
    for i in range(len(consumer_list[consume_type - 1])):
        if consumer_list[consume_type - 1][i] == worker_id:
            return True
    # 是否存在于执行序列
    for i in range(4):
        if robot_task[i][0] >= 0 and robot_task[i][2] == worker_id and worker_infos[robot_task[i][1]][0] == consume_type:
            return True
    # # 是否存在于任务序列
    # for i in range(len(task_list)):
    #     if task_list[i][2] == worker_id:
    #         return True
    # 是否存在于专属任务序列
    for i in range(4):
        for j in range(len(custom_task_list[i])):
            if custom_task_list[i][j][2] == worker_id and worker_infos[custom_task_list[i][j][1]][0] == consume_type:
                return True

    return False

# 目标工作台原材料是否已经完备
def isCompeleted(worker_id):
    worker_type = worker_infos[worker_id][0]
    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    hold_num = 0
    # 遍历依赖关系
    for j in range(9):
        # 当工作台需要某类型物品且其材料格并未持有该物品，并且不在消费者队列中，同时不存在对应的执行任务和待办任务运送该类物品到自身，则添加到消费者队列中
        if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '1':
            hold_num = hold_num + 1
            continue
        if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0':
            for i in range(4):
                if robot_task[i][0] != -1 and worker_infos[robot_task[i][1]][0] == j+1 and robot_task[i][2] == worker_id:
                    hold_num = hold_num + 1
                    break
            for i in range(4):
                for k in range(len(custom_task_list[i])):
                    if worker_infos[custom_task_list[i][k][1]][0] == j+1 and custom_task_list[i][k][2] == worker_id:
                        hold_num = hold_num + 1
                        break
    if hold_num == getNeedProductCount(worker_type):
        return True
    return False


# 读入工作台状态信息和机器人信息
def updateInfo():
    global worker_num
    global root_node
    global token

    # 读入工作台数量
    line = sys.stdin.readline()
    parts = line.split(' ')
    roun = int(parts[0])

    for i in range(len(finished_num)):
        finished_num[i] =  0

    # 更新工作台信息
    for i in range(roun):
        line = sys.stdin.readline()
        # 初始化/更新工作台信息
        if flag == False:
            worker_num = roun  # 更新工作台数量(不变)
            initWorkerInfo(line)  # 初始化工作台信息
        else:
            updateWorkerInfo(i, line)  # 更新工作台信息
    # if time > 8000 and haveSeven and worker_num == 25:
    #     token = -1
    #     root_node.id = -1

    # 判断是否需要更换7类工作重点
    if haveSeven and len(priority_list) > 1:
        if isCompeleted(priority_list[0]) and token == 0:
            root_node.id = priority_list[1]
            token = 1
        elif isCompeleted(priority_list[1]) and token == 1:
            root_node.id = priority_list[0]
            token = 0

    # 更新机器人信息
    for i in range(4):
        line = sys.stdin.readline()
        updateRobotInfo(i, line)

    if time < 8000:
        # 刷新生产者队列
        refreshProducerList2()
        # 刷新消费者队列
        refreshConsumerList2()
        complementSeven2()
    else:
        # 刷新生产者队列
        refreshProducerList()

        # 刷新消费者队列
        refreshConsumerList()
        complementSeven()


    # 刷新在产物品数量
    refreshOnProducingNum()

# 补充消费者队列
def complementSeven():
    for i in range(len(priority_list)):
        #print('7号工作台还有%d帧完成生产' % (worker_infos[priority_list[i]][3]),file=F)
        worker_id = priority_list[i]
        worker_type = 7
        holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
        holder_num = 0
        for j in range(9):
            # 当工作台需要某类型物品且其材料格并未持有该物品，并且不在消费者队列中，同时不存在对应的执行任务和待办任务运送该类物品到自身，则添加到消费者队列中
            if worker_type == 7 and depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '1':
                holder_num += 1
                continue
            if worker_type == 7 and depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0':
                for k in range(4):
                    if robot_task[k][2] == worker_id and worker_infos[robot_task[k][1]][0] == j+1 and calTimeRobot2Target(k,worker_id) < worker_infos[worker_id][3]/50-0.5:
                        holder_num += 1
                        break
                continue
        if worker_num == 25:
            if holder_num == 3 and worker_infos[i][3] >= 0 and worker_infos[i][3] <= 100:
                if not consumerIsOk(worker_id, 5):
                    consumer_list[4].append(worker_id)
            if holder_num == 3 and worker_infos[i][3] >= 0 and worker_infos[i][3] <= 220:
                if not consumerIsOk(worker_id, 6):
                    consumer_list[5].append(worker_id)

            if holder_num == 3 and worker_infos[i][3] >= 0 and worker_infos[i][3] <= 20:
                if not consumerIsOk(worker_id, 4):
                    consumer_list[3].append(worker_id)
        elif worker_num == 18:
            if holder_num == 3 and worker_infos[i][3] >= 0 and worker_infos[i][3] <= 200:
                if not consumerIsOk(worker_id, 5):
                    consumer_list[4].append(worker_id)
                if not consumerIsOk(worker_id, 6):
                    consumer_list[5].append(worker_id)

            if holder_num == 3 and worker_infos[i][3] >= 0 and worker_infos[i][3] <= 400:
                if not consumerIsOk(worker_id, 4):
                    consumer_list[3].append(worker_id)

def complementSeven2():
    for i in range(len(priority_list)):
        if not isInCurrentProducerGroup(i):
            continue
        #print('7号工作台还有%d帧完成生产' % (worker_infos[priority_list[i]][3]),file=F)
        worker_id = priority_list[i]
        worker_type = 7
        holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
        holder_num = 0
        for j in range(9):
            # 当工作台需要某类型物品且其材料格并未持有该物品，并且不在消费者队列中，同时不存在对应的执行任务和待办任务运送该类物品到自身，则添加到消费者队列中
            if worker_type == 7 and depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '1':
                holder_num += 1
                continue
            if worker_type == 7 and depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0':
                for k in range(4):
                    if robot_task[k][2] == worker_id and worker_infos[robot_task[k][1]][0] == j+1 and calTimeRobot2Target(k,worker_id) < worker_infos[worker_id][3]/50-0.5:
                        holder_num += 1
                        break
                continue
        if holder_num == 3 and worker_infos[i][3] >= 0 and worker_infos[i][3] <= 100:
            if not consumerIsOk(worker_id, 5):
                consumer_list[4].append(worker_id)
        if holder_num == 3 and worker_infos[i][3] >= 0 and worker_infos[i][3] <= 220:
            if not consumerIsOk(worker_id, 6):
                consumer_list[5].append(worker_id)

        if holder_num == 3 and worker_infos[i][3] >= 0 and worker_infos[i][3] <= 20:
            if not consumerIsOk(worker_id, 4):
                consumer_list[3].append(worker_id)



def calDistance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** (0.5)


def recursive_get(n):
    if n == 0:
        return ""
    return recursive_get(n // 2) + str(n % 2)

# 数字转二进制串
def numConvertBinaryList(num):
    binary = recursive_get(num);
    length = len(binary)
    for i in range(8 - length):
        binary = '0' + binary
    return binary


# 初始化
def initInfo():
    global worker_num
    global root_node
    global haveSeven
    # 初始化工作台数量
    worker_num = len(worker_infos)

    # 初始化节点距离图
    for i in range(worker_num):
        for j in range(worker_num):
            if (i == j):
                distance_graph[i][j] = 0
            else:
                distance = calDistance(worker_infos[i][1], worker_infos[i][2], worker_infos[j][1], worker_infos[j][2])
                distance_graph[i][j] = distance

    if haveSeven:
        for i in range(worker_num):
            if worker_infos[i][0] == 7:
                #更新中心点
                center[0] = worker_infos[i][1]
                center[1] = worker_infos[i][2]
                break

    if not haveSeven and haveNine:
        for i in range(worker_num):
            if worker_infos[i][0] == 9:
                center[0] = worker_infos[i][1]
                center[1] = worker_infos[i][2]
                break
    # 将所有7类节点放入优先队列
    for i in range(worker_num):
        if worker_infos[i][0] == 7:
            priority_list.append(i)

    if haveSeven and len(priority_list)>0:
        root_node = buildTreeStructureOf7(priority_list[0])

# 计算机器人赶到目标所需的时间
def calTimeRobot2Target(robot_id,worker_id):
    distance = calDistance(robot_infos[robot_id][7],robot_infos[robot_id][8],worker_infos[worker_id][1],worker_infos[worker_id][2])
    speed = 5
    # 加一秒是增加容错
    return distance/speed

# 刷新消费者队列
def refreshConsumerList():
    # 遍历所有工作台，更新消费者队列
    for i in range(worker_num):
        worker_type = worker_infos[i][0] # 工作台类型
        # 1，2，3类型的工作台不需要材料，因此没有消费需求
        if worker_type == 1 or worker_type == 2 or worker_type == 3:
            continue
        holder = numConvertBinaryList(worker_infos[i][4])[::-1]
        # 遍历依赖关系
        for j in range(9):
            # 当工作台需要某类型物品且其材料格并未持有该物品，并且不在消费者队列中，同时不存在对应的执行任务和待办任务运送该类物品到自身，则添加到消费者队列中
            if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0' and (not consumerIsOk(i, j + 1)):
                consumer_list[j].append(i)
            # if worker_type == 7 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
            #     3] >= 0 and worker_infos[i][3] <= 150:
            #     consumer_list[j].append(i)
            if worker_num == 25:
                if worker_type == 7 and j + 1 == 4 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][
                    6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
                    3] >= 0 and worker_infos[i][3] <= 20:
                    consumer_list[j].append(i)
                if worker_type == 7 and j + 1 == 5 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][
                    6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
                    3] >= 0 and worker_infos[i][3] <= 100:
                    consumer_list[j].append(i)
                if worker_type == 7 and j + 1 == 6 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][
                    6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
                    3] >= 0 and worker_infos[i][3] <= 220:
                    consumer_list[j].append(i)
            elif worker_infos == 18:
                if worker_type == 7 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][6] == 3 and (
                not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
                    3] >= 0 and worker_infos[i][3] <= 200:
                    consumer_list[j].append(i)
                if worker_type == 7 and j + 1 == 4 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][
                    6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
                    3] >= 0 and worker_infos[i][3] <= 400:
                    consumer_list[j].append(i)

def refreshConsumerList2():
    for i in range(len(consumer_list)):
        consumer_list[i].clear()

    # 遍历所有工作台，更新消费者队列
    for i in range(worker_num):
        worker_id = i
        worker_type = worker_infos[worker_id][0] # 工作台类型
        # 1，2，3类型的工作台不需要材料，因此没有消费需求
        if worker_type == 1 or worker_type == 2 or worker_type == 3:
            continue
        if not isInCurrentConsumerGroup(worker_id):
            continue
        holder = numConvertBinaryList(worker_infos[i][4])[::-1]
        # 遍历依赖关系
        for j in range(7):
            # 当工作台需要某类型物品且其材料格并未持有该物品，并且不在消费者队列中，同时不存在对应的执行任务和待办任务运送该类物品到自身，则添加到消费者队列中
            if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0' and (not consumerIsOk(i, j + 1)):
                consumer_list[j].append(worker_id)
                continue
            # if worker_type == 7 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
            #     3] >= 0 and worker_infos[i][3] <= 130:
            #     consumer_list[j].append(i)
            if worker_type == 7 and j + 1 == 4 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][
                6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
                3] >= 0 and worker_infos[i][3] <= 10:
                consumer_list[j].append(i)
            if worker_type == 7 and j + 1 == 5 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][
                6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
                3] >= 0 and worker_infos[i][3] <= 80:
                consumer_list[j].append(i)
            if worker_type == 7 and j + 1 == 6 and depend_graph[j][worker_type - 1] == 1 and worker_infos[i][
                6] == 3 and (not consumerIsOk(i, j + 1)) and worker_infos[i][5] == 0 and worker_infos[i][
                3] >= 0 and worker_infos[i][3] <= 100:
                consumer_list[j].append(i)

def isInCurrentConsumerGroup(worker_id):
    for i in range(len(consumer_group[token])):
        if consumer_group[token][i] == worker_id:
            return True
    return False

def isInCurrentProducerGroup(worker_id):
    for i in range(len(producer_group[token])):
        if producer_group[token][i] == worker_id:
            return True
    return False

# 预判材料格剩余清空时间
def predictSourceClearTime(worker_id):
    worker_type = worker_infos[worker_id][0]  # 工作台类型
    need_time = 0# 剩余清空时间
    # 1，2，3类型的工作台不需要材料，因此没有消费需求
    if worker_type == 1 or worker_type == 2 or worker_type == 3:
        return need_time
    # 如果工作台现在持有所有所需材料且当前未持有产物时，剩余的清空时间就是该工作台完成当前生产的时间
    if getNeedProductCount(worker_type) == worker_infos[worker_id][6] and worker_infos[worker_id][5] == 0:
        time = worker_infos[worker_id][3]/50
        return time

    # 如果工作台现在持有所有所需材料且当前持有产物时，剩余的清空时间就是该工作台产物被取走的时间
    # if getNeedProductCount(worker_type) == worker_infos[worker_id][6] and worker_infos[worker_id][5] == 1:
    #     for i in range(4):
    #
    # 如果工作台现在需要材料时，剩余的清空时间就是机器人将剩余材料送到工作台的时间
    # holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    # # 遍历依赖关系
    # for j in range(9):
    #     # 当工作台并持有该类物品时，不考虑
    #     if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '1':
    #         continue
    #     # 即将进行集齐材料的工作台会马上进入生产状态，它的材料格会被清空
    #     if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '1' and (not consumerIsOk(i, j + 1)):
    #         pass

# 刷新当前场上在产物品数
def refreshOnProducingNum():
    # 清空上一帧统计的数量
    for i in range(len(on_producing_record)):
        on_producing_record[i] = 0

    # 若该工作台正在生产，这将该工作台生产物品类型对应的在产数量记录加一
    # 若该工作台持有对应类型物品也需要计入统计
    for i in range(worker_num):
        work_type = worker_infos[i][0]
        if worker_infos[i][3] >= 0:
            on_producing_record[work_type - 1] = on_producing_record[work_type - 1] + 1


# 插入任务，根据权值排序，升序排列、选择插入
def insertTask(weight, start, target):
    if len(task_list) == 0:
        task_list.append([weight, start, target])
        return
    for i in range(len(task_list)):
        if (task_list[i][0] < weight):
            task_list.insert(i, [weight, start, target])
            return
    task_list.append([weight, start, target])


# 统计目标工作台所需材料且未被分配的数量
def getNeedProductNumWithoutAssigned(worker_id):
    worker_type = worker_infos[worker_id][0]
    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    num = getNeedProductCount(worker_type)
    for j in range(9):
        # 如果目前工作台持有该原材料，则数量-1 且没有相应的任务或在执行任务则生成对应的任务
        if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '1':
            num = num - 1
            continue
        # 如果目前工作台未持有该原材料，但存在相应的任务，则数量-1
        if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0' and consumerIsExistInTaskList(worker_id,
                                                                                                        worker_type):
            num = num - 1
            continue
        # 如果目前工作台未持有该原材料，但存在相应的执行任务，则数量-1
        if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0' and consumerIsExistInRobotList(worker_id,
                                                                                                         worker_type):
            num = num - 1
            continue
        # 如果目前工作台未持有该原材料，但存在相应的执行任务，则数量-1
        if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0' and consumerIsExistInCustomList(worker_id,
                                                                                                          worker_type):
            num = num - 1
            continue
    return num

# 获取需要worker_type类型物品工作台中在产以及已经完成生产的数量最小的类型
def getMinTypeNeeded(worker_id):
    # 获取需要worker_type类型物品工作台中在产以及已经完成生产的数量最小的类型
    worker_type = worker_infos[worker_id][0]# worker_id对应的工作台类型
    # 只考虑123到456的依赖情况
    if worker_type > 3:
        return -1
    min_value = 100 #场上需要worker_type类型物品的工作台类型中最少的值
    min_type = -1#场上需要worker_type类型物品的工作台类型
    for i in range(9):
        if depend_graph[worker_type - 1][i] == 1:
            temp_worker_type = i + 1 #可以接收worker_id的类型
            # 只考虑123到456的依赖情况
            if temp_worker_type >= 7:
                if min_type == -1:
                    min_type = temp_worker_type
                    min_value = 0
                break
            # 统计场上temp_worker_type物品的数量
            # 统计场上temp_worker_type物品正在生产的数量
            num = on_producing_record[temp_worker_type - 1]
            # print('在产的%d类物品有%d个' % (temp_worker_type,on_producing_record[temp_worker_type - 1]),file=F)
            # 统计已经完成生产的数量
            num = num + finished_num[temp_worker_type - 1]
            # print('已经完成生产的%d类物品有%d个' % (temp_worker_type,finished_num[temp_worker_type - 1]),file=F)
            # 统计该类型物品已经被取走送往卖点的数量
            for k in range(4):
                if robot_task[k][0] != -1 and worker_infos[robot_task[k][1]][0] == worker_type and worker_infos[robot_task[k][2]][0] == temp_worker_type:
                    num = num + 1
                if robot_task[k][0] == 1 and worker_infos[robot_task[k][1]][0] == temp_worker_type:
                    num = num + 1
            # print('正在运送%d类物品到%d类工作台的数量有%d个' % (worker_type,temp_worker_type, num - finished_num[temp_worker_type - 1]- on_producing_record[temp_worker_type - 1]) , file=F)
            # 统计该类型工作台所需所有原材料都已经完成任务分配的元素数量
            for j in range(worker_num):
                if temp_worker_type == worker_infos[j][0] and isHoldWorkerType(j,worker_type):
                    num = num + 1
                if 7 == worker_infos[j][0] and isHoldWorkerType(j, temp_worker_type):
                    num = num + 1
            # print('当前场上%d类物品类型%d个' % (temp_worker_type, num), file=F)
            if num < min_value:
                min_value = num
                min_type = temp_worker_type
    #print('*****************************************', file=F)
    # print('%d类型的物品正在匹配消费者，当前场上最少的物品类型是%d，有%d个' % (worker_type,min_type,min_value),file=F)

    #确保不会因为4，5，6数量过多而过于离散
    if min_value > 4:
        min_type = -1
    return min_type

# 计算需要worker_type物品中数量最少的类型
def getMinTypeNeeded2(worker_type):
    min_value = 999  # 场上需要worker_type类型物品的工作台类型中最少的值
    min_type = -1  # 场上需要worker_type类型物品的工作台类型
    for i in range(9):
        if depend_graph[worker_type - 1][i] == 1:
            temp_worker_type = i + 1  # 可以接收worker_id的类型
            # 只考虑123到456的依赖情况
            if temp_worker_type >= 7:
                if min_type == -1:
                    min_type = temp_worker_type
                    min_value = 0
                break
            # 统计场上temp_worker_type物品正在生产的数量
            num = on_producing_record[temp_worker_type - 1]
            # 统计已经完成生产的数量
            num = num + finished_num[temp_worker_type - 1]
            for k in range(4):
                # 统计运送worker_type类型物品到temp_worker_type类型工作台的正在执行的任务的数量
                if robot_task[k][0] != -1 and worker_infos[robot_task[k][1]][0] == worker_type and \
                        worker_infos[robot_task[k][2]][0] == temp_worker_type:
                    num = num + 1
                # 统计该类型物品已经被取走送往卖点的数量
                if robot_task[k][0] == 1 and worker_infos[robot_task[k][1]][0] == temp_worker_type:
                    num = num + 1
                # 统计运送worker_type类型物品到temp_worker_type类型工作台的任务的专属任务的数量
                for t in range(len(custom_task_list[k])):
                    if worker_infos[custom_task_list[k][t][1]][0] == worker_type and \
                            worker_infos[custom_task_list[k][t][2]][0] == temp_worker_type:
                        num = num + 1
            for j in range(worker_num):
                # 统计456手中持有的worker_type类型物品的数量
                if temp_worker_type == worker_infos[j][0] and isHoldWorkerType(j, worker_type):
                    num = num + 1
                # 统计7手中持有的temp_worker_type类型物品的数量
                if 7 == worker_infos[j][0] and isHoldWorkerType(j, temp_worker_type):
                    num = num + 1
            if num < min_value:
                min_value = num
                min_type = temp_worker_type

    #确保不会因为4，5，6数量过多而过于离散
    if min_value > 4:
        min_type = -1
    return min_type

# 获取需要worker_type类型物品工作台中在产以及已经完成生产的数量最小的类型的数量
def getMinTypeNumNeededOfType(worker_type):
    # 只考虑123到456的依赖情况
    if worker_type > 3:
        return -1
    min_value = 999 #场上需要worker_type类型物品的工作台类型中最少的值
    min_type = -1#场上需要worker_type类型物品的工作台类型
    for i in range(9):
        if depend_graph[worker_type - 1][i] == 1:
            temp_worker_type = i + 1 #可以接收worker_id的类型
            # 只考虑123到456的依赖情况
            if temp_worker_type >= 7:
                if min_type == -1:
                    min_type = temp_worker_type
                    min_value = 0
                break
            # 统计场上temp_worker_type物品正在生产的数量
            num = on_producing_record[temp_worker_type - 1]
            # 统计已经完成生产的数量
            num = num + finished_num[temp_worker_type - 1]
            for k in range(4):
                # 统计运送worker_type类型物品到temp_worker_type类型工作台的正在执行的任务的数量
                if robot_task[k][0] != -1 and worker_infos[robot_task[k][1]][0] == worker_type and worker_infos[robot_task[k][2]][0] == temp_worker_type:
                    num = num + 1
                # 统计该类型物品已经被取走送往卖点的数量
                if robot_task[k][0] == 1 and worker_infos[robot_task[k][1]][0] == temp_worker_type:
                    num = num + 1
                # 统计运送worker_type类型物品到temp_worker_type类型工作台的任务的专属任务的数量
                for t in range(len(custom_task_list[k])):
                    if worker_infos[custom_task_list[k][t][1]][0] == worker_type and worker_infos[custom_task_list[k][t][2]][0] == temp_worker_type:
                        num = num + 1
            for j in range(worker_num):
                # 统计456手中持有的worker_type类型物品的数量
                if temp_worker_type == worker_infos[j][0] and isHoldWorkerType(j, worker_type):
                    num = num + 1
                # 统计7手中持有的temp_worker_type类型物品的数量
                if 7 == worker_infos[j][0] and isHoldWorkerType(j, temp_worker_type):
                    num = num + 1
            #print('%d类型工作台有%d个%d' % (temp_worker_type,num,worker_type),file=F)
            if num < min_value:
                min_value = num
                min_type = temp_worker_type
    return min_value

#获取目标类型最迫切需要的材料
def getWantedProductOfWorkerType(worker_type):
    product_num = []#worker_type所持有的各类型的材料总数
    for i in range(9):
        need_type = i + 1
        num = [need_type,0]
        if depend_graph[i][worker_type-1] == 1:
            for j in range(worker_num):
                if worker_infos[j][0] == worker_type and isHoldWorkerType(j,need_type):
                    num[1] += 1
            for j in range(4):
                if robot_task[j][0] != -1 and worker_infos[robot_task[j][1]][0] == need_type and worker_infos[robot_task[j][2]][0] == worker_type:
                    num[1] += 1
                for t in range(len(custom_task_list[j])):
                    if worker_infos[custom_task_list[j][t][1]][0] == need_type and worker_infos[custom_task_list[j][t][2]][0] == worker_type:
                        num[1] += 1
            product_num.append(num)
    min_value = 999
    min_type = -1
    for i in range(len(product_num)):
        if min_value > product_num[i][1]:
            min_type = product_num[i][0]
            min_value = product_num[i][1]
    return min_type


    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    if depend_graph[product_type - 1][worker_type - 1] == 0:
        return False
    # 如果目前工作台持有该原材料，则数量-1 且没有相应的任务或在执行任务则生成对应的任务
    if depend_graph[product_type - 1][worker_type - 1] == 1 and holder[product_type] == '1':
        return False


def generateTaskRealTime(robot_id):
    global time
    task = [-1, -1] #0:采购点id，售卖点id
    for i in range(3):
        prior_type = -1#优先运送的类型
        num = 100
        if i == 2:
            min_type_456 = getMinTypeOf456()
            if min_type_456 != -1:
                prior_type = getWantedProductOfWorkerType(min_type_456)

        producerList = [] # 对生产者价值队列进行排序
        # 针对机器人当前位置对i级销售者价值队列进行权重排序
        for j in range(len(value_producer_list[i])):
            temp_buy_id = value_producer_list[i][j] # 可用的买点id
            temp_buy_type = worker_infos[temp_buy_id][0]  # 买点类型
            robot_x = robot_infos[robot_id][7] # 机器人x坐标
            robot_y = robot_infos[robot_id][8] # 机器人y坐标
            buy_x = worker_infos[temp_buy_id][1] # 买点x坐标
            buy_y = worker_infos[temp_buy_id][2] # 买点y坐标
            distance_r2p = calDistance(robot_x, robot_y, buy_x, buy_y) # 计算机器人和购买点的距离
            distance_p2center = calDistance(center[0], center[1], worker_infos[temp_buy_id][1], worker_infos[temp_buy_id][2])# 计算买点离中心点的距离
            weight_r2p = distance_r2p * 0.7 + distance_p2center * 0 # 计算综合权值，越小的优先级越大
            # 对于456类型的工作台来说，如果自身类型是root_node7类工作台所需的，则需要优先安排
            if i == 1 and haveSeven and isLackProductType(root_node.id,temp_buy_type):
                weight_r2p = weight_r2p*0.5
            # 对于123类型的工作台来说，如果自身类型是全局456中类型数量最少的工作台所需的，则需要优先安排
            if i == 2 and prior_type == temp_buy_type:
                weight_r2p = weight_r2p * 0.2
            producer = [weight_r2p, temp_buy_id]# 用于插入到producerList,后面与消费者列表进行综合配对选择
            # 将生产者工作台按权值进行排序(升序)
            index = 0
            for k in range(len(producerList)):
                if producer[0] < producerList[k][0]:
                    producerList.insert(k, producer)
                    index += 1
                    break
            if index == len(producerList):
                producerList.append(producer)

        # 遍历排好序的生产者列表，从权值小的开始寻找最适配的卖点，直到找到配对的
        for m in range(len(producerList)):
            buy_id = producerList[m][1] # 买点id
            buy_type = worker_infos[buy_id][0]  # 要购买的类型
            min_weight_p2c = 999  # 机器人到购买点的最小权值
            sell_id = -1 # 卖点id，值为-1时视为未找到与买点适配的卖点
            min_consumer_type = getMinTypeOf456() # 当前场上需要buy_type类型物品的工作台中，数量最少的类型
            # 根据找到的购买点为其寻找最合适的出售点
            for j in range(len(consumer_list[buy_type - 1])):
                temp_sell_id = consumer_list[buy_type - 1][j]# 可用的卖点
                temp_sell_type = worker_infos[temp_sell_id][0]# 卖点的类型
                distance_p2c = distance_graph[buy_id][temp_sell_id]# 计算买点到可用卖点的距离
                holder_num = worker_infos[temp_sell_id][6]# 目标销售点持有物品数量
                # 物品在运送途中的也被视为其拥有的
                for n in range(4):
                    if robot_task[n][0] != -1 and robot_task[n][2] == temp_sell_id:
                        holder_num = holder_num + 1
                    for p in range(len(custom_task_list[n])):
                        if custom_task_list[n][p][2] == temp_sell_id:
                            holder_num = holder_num + 1
                if time > 7800 and temp_sell_type == 4 and worker_num == 18:
                    continue
                distance_c2center = calDistance(center[0], center[1], worker_infos[temp_sell_id][1],worker_infos[temp_sell_id][2])# 计算可用卖点到中心点的距离
                # 计算中心点权值
                weight_p2c = distance_p2c * 1 + distance_c2center * 0.3 + (getNeedProductCount(temp_sell_type)-holder_num)*10
                # 出于均衡，对于最少的类型我们提升其权重
                if min_consumer_type == temp_sell_type:
                    weight_p2c = weight_p2c * 0.1
                # 对于目标7类工作台，全力生产
                if 7 == temp_sell_type and temp_sell_id == root_node.id:
                    weight_p2c = 0
                # 得到权值最小的工作台目标
                if weight_p2c < min_weight_p2c:
                    min_weight_p2c = weight_p2c
                    sell_id = temp_sell_id
            # 最后1000帧开始判断任务是否可执行完，对于无法完成的任务不与分配
            if time > 8000 and (not canFinish(robot_id,buy_id,sell_id)):
                continue
            # 未找到合适的售卖工作台
            if sell_id == -1:
                continue
            else:
                #生成任务
                task[0] = buy_id
                task[1] = sell_id
                #print('为%d号机器人生成实时任务从%d运输%d类物品到%d号工作台，目标工作台类型为%d' % (robot_id, buy_id, worker_infos[buy_id][0], sell_id, worker_infos[sell_id][0]), file=F)
                removeProducerFromValueProducerList(buy_id)
                removeConsumerFromConsumerList(sell_id,buy_type)
                return task
    return task

def generateTaskRealTime2(robot_id):
    task = [-1, -1] #0:采购点id，售卖点id
    producerList = []
    robot_x = robot_infos[robot_id][7]  # 机器人x坐标
    robot_y = robot_infos[robot_id][8]  # 机器人y坐标
    for i in range(3):
        for j in range(len(value_producer_list[i])):
            temp_buy_id = value_producer_list[i][j]  # 可用的买点id
            buy_x = worker_infos[temp_buy_id][1]  # 买点x坐标
            buy_y = worker_infos[temp_buy_id][2]  # 买点y坐标
            distance_r2p = calDistance(robot_x, robot_y, buy_x, buy_y)  # 计算机器人和购买点的距离
            if distance_r2p < 30:
                producer = [distance_r2p, temp_buy_id]  # 用于插入到producerList,后面与消费者列表进行综合配对选择
                producerList.append(producer)
    max_meter_wage = 0
    for i in range(len(producerList)):
        buy_id = producerList[i][1]  # 买点id
        buy_type = worker_infos[buy_id][0]  # 要购买的类型
        distance_r2p = producerList[i][0]
        task_profit = profit[buy_type-1]#任务利润
        for j in range(len(consumer_list[buy_type - 1])):
            temp_sell_id = consumer_list[buy_type - 1][j]  # 可用的卖点
            temp_sell_type = worker_infos[temp_sell_id][0]  # 卖点的类型
            distance_p2c = distance_graph[buy_id][temp_sell_id]  # 计算买点到可用卖点的距离
            holder_num = worker_infos[temp_sell_id][6]  # 目标销售点持有物品数量
            #task_profit += holder_num * 250
            # distance_c2center = calDistance(center[0], center[1], worker_infos[temp_sell_id][1],worker_infos[temp_sell_id][2])  # 计算可用卖点到中心点的距离
            # if distance_c2center != 0:
            #     task_profit += 1000 / distance_c2center
            meter_wage = task_profit / (distance_r2p + distance_p2c)
            if time > 8000 and (not canFinish(robot_id,buy_id,temp_sell_id)):
                continue
            if meter_wage > max_meter_wage:
                max_meter_wage = meter_wage
                task[0] = buy_id
                task[1] = temp_sell_id
    if max_meter_wage >0 and task[0]!= -1 and task[1] !=-1:
        removeProducerFromValueProducerList(task[0])
        removeConsumerFromConsumerList(task[1], worker_infos[task[0]][0])

    return task

# 生成指令
def instruct(robot_id):
    target_id = -1
    task_type = robot_task[robot_id][0]
    if task_type == 0:
        target_id = robot_task[robot_id][1]
    elif task_type == 1:
        target_id = robot_task[robot_id][2]
    # 生成指令
    if worker_num == 25:
        physics2.doInstruct(robot_id, robot_infos[robot_id][0], robot_infos[robot_id][6],
                           robot_infos[robot_id][7], robot_infos[robot_id][8], robot_infos[robot_id][4],
                           robot_infos[robot_id][9], robot_infos[robot_id][10], target_id, worker_infos[target_id][1],
                           worker_infos[target_id][2], task_type, robot_infos, worker_num)
    elif worker_num == 18:
        physics4.doInstruct(robot_id, robot_infos[robot_id][0], robot_infos[robot_id][6],
                           robot_infos[robot_id][7], robot_infos[robot_id][8], target_id, worker_infos[target_id][1],
                           worker_infos[target_id][2], task_type)

    #
    #     def doInstruct(robot_id, plat_id,  direction, robot_x, robot_y, target_id, target_x, target_y,
    #                    task_type):

def standardization(angle):
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    return angle


def CalculateAngle(direction, target_x, target_y):
    angle = math.atan2(target_y, target_x) - direction
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    return angle


def CheckCrush(robot1_id, robot1_direction, robot1_x, robot1_y, robot1_Vx, robot1_Vy, robot2_id, robot2_direction,
               robot2_x, robot2_y, robot2_Vx, robot2_Vy):
    if robot1_id == robot2_id:
        return
    line_angle = math.atan2(robot2_y - robot1_y, robot2_x - robot1_x)  # 以机器人1号坐标为起点到机器人二号坐标的向量，以弧度表示
    unline_angle = line_angle + math.pi if line_angle < 0 else line_angle - math.pi  # line_angle的反向向量弧度
    # 预测机制_预测t秒后的世界线
    t = 0.3
    # t秒后的机器人1的位置
    (x1, y1) = (robot1_x + robot1_Vx * t, robot1_y + robot1_Vy * t)
    # t秒后的机器人2的位置
    (x2, y2) = (robot2_x + robot2_Vx * t, robot2_y + robot2_Vy * t)
    Rdistance = ((robot2_y - robot1_y) ** 2 + (robot2_x - robot1_x) ** 2) ** 0.5
    betweenRobotAngle = standardization(robot1_direction - robot2_direction)  # 机器人朝向之间的标准化
    # 两机器人的当前速度
    robot1_V = (robot1_Vx ** 2 + robot1_Vy ** 2) ** 0.5
    robot2_V = (robot2_Vx ** 2 + robot2_Vy ** 2) ** 0.5
    if ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5 < 1.06:  # ＞1说明没有碰到了
        checkSpeed1 = 4
        if abs(betweenRobotAngle) > math.pi / 3:
            if robot1_x != robot2_x:
                k = (robot1_y - robot2_y) / (robot1_x - robot2_x)
                if k > 0:
                    sys.stdout.write('rotate %d %f\n' % (robot1_id, math.pi))
                    sys.stdout.write('rotate %d %f\n' % (robot2_id, math.pi))
                    sys.stdout.write('forward %d %d\n' % (robot1_id, checkSpeed1))
                    sys.stdout.write('forward %d %d\n' % (robot2_id, checkSpeed1))
                else:
                    sys.stdout.write('rotate %d %f\n' % (robot1_id, -math.pi))
                    sys.stdout.write('rotate %d %f\n' % (robot2_id, -math.pi))
                    sys.stdout.write('forward %d %d\n' % (robot1_id, checkSpeed1))
                    sys.stdout.write('forward %d %d\n' % (robot2_id, checkSpeed1))
            else:
                sys.stdout.write('rotate %d %f\n' % (robot1_id, math.pi))
                sys.stdout.write('rotate %d %f\n' % (robot2_id, math.pi))
                sys.stdout.write('forward %d %d\n' % (robot1_id, checkSpeed1))
                sys.stdout.write('forward %d %d\n' % (robot2_id, checkSpeed1))
        # else:
        #     if robot1_id < robot2_id:
        #         untangle = standardization(unline_angle - robot1_direction)  # 序号小的机器人远离序号大的机器人
        #         if untangle > 0:
        #             sys.stdout.write('rotate %d %f\n' % (robot1_id, math.pi))
        #             sys.stdout.write('forward %d %d\n' % (robot1_id, 0))
        #         else:
        #             sys.stdout.write('rotate %d %f\n' % (robot1_id, -math.pi))
        #             sys.stdout.write('forward %d %d\n' % (robot1_id, 0))
    # if Rdistance < 2 and abs(betweenRobotAngle) < math.pi/9 and abs(standardization(robot1_direction-line_angle))>math.pi/1.1:
        # sys.stdout.write('forward %d %d\n' % (robot1_id, robot2_V/1.1))
#
# 判断任务是否可以在结束前完成
def canFinish(robot_id,buy_id,sell_id):
    distance_b2s = distance_graph[buy_id][sell_id]# 买点和卖点的距离
    distance_r2b = calDistance(robot_infos[robot_id][7], robot_infos[robot_id][8], worker_infos[buy_id][1], worker_infos[buy_id][2])# 机器人和买点的距离
    leave_time = (9000 - time)/50 # 计算剩余时间(秒)
    redundance = 1# 冗余时间,增加容错
    avg_time = 5.5# 平均行驶速度
    distance = distance_b2s +distance_r2b
    if (distance/avg_time + redundance) < leave_time:
        return True
    else:
        return False


# 判断目标机器人是否完成当前阶段任务
def updateRobotTaskInfo(robot_id):
    task_phase = robot_task[robot_id][0]
    if task_phase == 0:
        # 如果机器人身上携带的物品类型与采购工作台的类型一致时表示采购完成，更新任务阶段到售卖阶段
        if robot_infos[robot_id][1] == worker_infos[robot_task[robot_id][1]][0]:
            robot_task[robot_id][0] = 1
    elif task_phase == 1:
        # 如果机器人身上携带的物品类型与采购工作台的类型不一致时表示售卖完成，更新任务阶段到完成任务
        if robot_infos[robot_id][1] != worker_infos[robot_task[robot_id][1]][0]:
            robot_task[robot_id][0] = -1

    else:
        return


# 更新机器人的任务完成情况
def updateRobotTask():
    for i in range(4):
        updateRobotTaskInfo(i)

# 任务执行
def exec():
    for i in range(4):
        # 判断机器人当前是否被分派了任务
        if robot_task[i][0] == -1 and time > 8700:
            sys.stdout.write('forward %d %d\n' % (i, 1))
            sys.stdout.write('rotate %d %f\n' % (i, 1))
        elif robot_task[i][0] == -1:
            pass
        else:
            instruct(i)


# 为机器人分派任务并执行操作
def assignTask():
    for i in range(4):
        # 判断机器人当前是否正在执行任务
        if robot_task[i][0] == -1:
            # 为机器人生成任务
            if len(custom_task_list[i]) > 0:
                if time > 8000 and (not canFinish(i, custom_task_list[i][0][1], custom_task_list[i][0][2])):
                    del custom_task_list[i][0]
                    continue
                robot_task[i][0] = 0
                robot_task[i][1] = custom_task_list[i][0][1]
                robot_task[i][2] = custom_task_list[i][0][2]
                del custom_task_list[i][0]
            else:
                task = None
                if time < 8000:
                    task = generateTaskRealTime(i)
                else:
                    task = generateTaskRealTime2(i)
                if task[0] == -1 or task[1] == -1:
                    continue
                robot_task[i][0] = 0
                robot_task[i][1] = task[0]
                robot_task[i][2] = task[1]


# 判断目标工作台是否缺某类型的原材料,并且该材料也未被纳入当前执行队列
def isLackProductType(worker_id, product_type):
    worker_type = worker_infos[worker_id][0]
    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    if depend_graph[product_type - 1][worker_type - 1] == 0:
        return False
    # 如果目前工作台持有该原材料，则数量-1 且没有相应的任务或在执行任务则生成对应的任务
    if depend_graph[product_type - 1][worker_type - 1] == 1 and holder[product_type] == '1':
        return False
    # 如果目前工作台未持有该原材料，但存在相应的任务，则数量-1
    # if depend_graph[product_type - 1][worker_type - 1] == 1 and holder[
    #     product_type] == '0' and consumerIsExistInTaskList(worker_id, product_type):
    #     return False
    # 如果目前工作台未持有该原材料，但存在相应的执行任务，则数量-1
    if depend_graph[product_type - 1][worker_type - 1] == 1 and holder[
        product_type] == '0' and consumerIsExistInRobotList(worker_id, product_type):
        return False
    # 如果目前工作台未持有该原材料，但存在相应的执行任务，则数量-1
    if depend_graph[product_type - 1][worker_type - 1] == 1 and holder[
        product_type] == '0' and consumerIsExistInCustomList(worker_id, product_type):
        return False
    return True




# 为指定工作台生成任务
def generateTaskForWorker(worker_id):
    worker_type = worker_infos[worker_id][0]
    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    count = getNeedProductCount(worker_type)  # 获取工作台所需的原材料数
    for j in range(9):
        # 如果目前工作台未持有该原材料，且没有相应的任务或在执行任务则生成对应的任务
        if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0' and consumerIsExistInTaskList(worker_id,
                                                                                                        worker_type) and consumerIsExistInRobotList(
                worker_id, worker_type):
            pass


# 目标工作台所需的原材料数
def getNeedProductCount(worker_type):
    count = 0
    for i in range(9):
        if depend_graph[i][worker_type - 1] == 1:
            count = count + 1
    return count

# 任务列表中是否存在出售点为worker_id，且出售类型为worker_type的任务
def consumerIsExistInTaskList(worker_id, worker_type):
    for i in range(len(task_list)):
        if task_list[i][2] == worker_id and worker_infos[task_list[i][1]][0] == worker_type:
            return True
    return False

def getIndexOfTask(worker_id, worker_type):
    for i in range(len(task_list)):
        if task_list[i][2] == worker_id and worker_infos[task_list[i][1]][0] == worker_type:
            return i
    return -1


# 执行列表中是否存在出售点为worker_id，且出售类型为worker_type的任务
def consumerIsExistInRobotList(worker_id, worker_type):
    for i in range(4):
        if robot_task[i][2] == worker_id and worker_infos[robot_task[i][1]][0] == worker_type:
            return True
    return False

# 执行列表中是否存在出售点为worker_id，且出售类型为worker_type的任务
def producerIsExistInRobotList(worker_id):
    for i in range(4):
        if robot_task[i][1] == worker_id and robot_task[i][0] == 0:
            return True
    return False

# 执行列表中是否存在出售点为worker_id，且出售类型为worker_type的任务
def producerIsExistInCustomTaskList(worker_id):
    for i in range(4):
        for j in range(len(custom_task_list[i])):
            if custom_task_list[i][j][1] == worker_id:
                return True
    return False

# 执行列表中是否存在出售点为worker_id
def producerIsExistInValueList(worker_id):
    worker_type = worker_infos[worker_id][0]
    if worker_type == 1 or worker_type == 2 or worker_type == 3:
        for i in range(len(value_producer_list[2])):
            if value_producer_list[2][i] == worker_id:
                return True
    elif worker_type == 4 or worker_type == 5 or worker_type == 6:
        for i in range(len(value_producer_list[1])):
            if value_producer_list[1][i] == worker_id:
                return True
    elif worker_type == 7:
        for i in range(len(value_producer_list[0])):
            if value_producer_list[0][i] == worker_id:
                return True
    return False

# 专属执行列表中是否存在出售点为worker_id，且出售类型为worker_type的任务
def consumerIsExistInCustomList(worker_id, worker_type):
    for i in range(4):
        for j in range(len(custom_task_list[i])):
            if custom_task_list[i][j][2] == worker_id and worker_infos[custom_task_list[i][j][1]][0] == worker_type:
                return True
    return False



# 将任务分配给最合适的机器人专属任务队列
def addToCustomTaskList(task):
    global custom_robot_id
    # 如果任务是运送7类物品，则赋给任务交付地点离物品最近的机器人
    # if worker_infos[task[1]][0] == 7:
    #     min_distance = 100
    #     r_id = -1
    #     for i in range(4):
    #         distance = calDistance(worker_infos[robot_task[i][2]][1], worker_infos[robot_task[i][2]][1], worker_infos[task[1]][1], worker_infos[task[1]][2])
    #         if distance < min_distance:
    #             r_id = i
    #         custom_task_list[r_id].insert(0,task)
    # else:
    custom_task_list[custom_robot_id].append(task)
    custom_robot_id = (custom_robot_id + 1) % 4

# 只适用于7类工作台
def intervene():
    for i in range(len(priority_list)):
        # 如果该7类工作台只剩余1一个材料，且未进入执行队列，则进行干预
        worker_id = priority_list[i]
        if (3 - worker_infos[worker_id][6]) == 1:
            # 找到当前7类工作台所需要的材料类型
            worker_type = getLackedProductForWorkerId(worker_id)[0]
            # 判断该类型是否存在对应的执行任务
            if consumerIsExistInRobotList(worker_id,worker_type):
                return
            # 判断该类型是否存在对应的专属任务
            if consumerIsExistInCustomList(worker_id,worker_type):
                return
            # 生成一个对应的任务进行处理
            min_distance = 100
            min_id = -1
            if len(value_producer_list[1]) > 0:
                for j in range(len(value_producer_list[1])):
                    temp_worker_id = value_producer_list[1][j]
                    temp_worker_type = worker_infos[temp_worker_id][0]
                    sell_x = worker_infos[worker_id][1]
                    sell_y = worker_infos[worker_id][2]
                    buy_x = worker_infos[temp_worker_id][1]
                    buy_y = worker_infos[temp_worker_id][2]
                    distance = calDistance(buy_x,buy_y,sell_x,sell_y)
                    if temp_worker_type == worker_type and distance < min_distance:
                        min_distance = distance
                        min_id = temp_worker_id
            if min_id != -1:
                task = [0, min_id, worker_id]
                addToCustomTaskList(task)
                consumer_list[worker_infos[min_id][0]-1].remove(worker_id)
                value_producer_list[1].remove(min_id)

# 获取目标工作台还未放入材料格的原材料类型
def getLackedProductForWorkerId(worker_id):
    worker_type = worker_infos[worker_id][0]
    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    result = []

    if worker_type == 1 or worker_type == 2 or worker_type == 3:
        return result

    for j in range(9):
        # 如果目前工作台未持有该原材料，且没有相应的任务或在执行任务则生成对应的任务
        if depend_graph[j][worker_type - 1] == 1 and holder[j + 1] == '0':
            result.append(j+1)

    return result

# 建立从7开始自顶向下的依赖树结构
def buildTreeStructureOf7(worker_id):
    worker_type = worker_infos[worker_id][0]
    father = Node(worker_id,worker_type,0)
    for i in range(9):
        if depend_graph[i][worker_type-1] == 1:
            son_type = i + 1 #子节点的工作台类型
            son_id = findNearestWokerForType(worker_id,son_type) #找到son_type类型离worker_id最近的工作台
            node = buildTreeStructureOf7(son_id)
            father.addSon(node)
    return father

# 根据树结构生成任务(同一时间只能有一层的任务)
def generateTreeTask(node):
    allReady = True
    sell_id = node.id
    for i in range(node.son_num):
        # 如果需要的子工作台还未准备好物品，同时自身也没有这类物品则先准备子工作台的物品
        #if (not producerIsExistInValueList(node.sons[i].id)) and (not isHoldWorkerType(sell_id,node.sons[i].type)):
        # 工作台是否准备好消费目标类型的物品
        if (not consumerIsExistInConsumerList(sell_id,node.sons[i].type)):
            continue
        if (not producerIsExistInValueList(node.sons[i].id)):
            # allReady = False
            # print('没有%d，需要造%d' %(node.sons[i].id,node.sons[i].id),file=F)
            generateTreeTask(node.sons[i])
        else:
            buy_id = node.sons[i].id
            buy_type = node.sons[i].type
            if taskIsInExecuting(buy_id, sell_id):
                # print('已经有从%d运送%d类物品到%d的任务正在执行中了' % (buy_id, buy_type,sell_id), file=F)
                continue
            if taskIsExistInCustomTaskList(buy_id, sell_id):
                # print('已经有从%d运送%d类物品到%d的任务正在专属队列中了' % (buy_id, buy_type, sell_id), file=F)
                continue
            task = [0, buy_id, sell_id]
            # print('生成了从%d运送%d类物品到%d的专属任务专属' % (buy_id, buy_type, sell_id), file=F)
            removeProducerFromValueProducerList(buy_id)
            removeConsumerFromConsumerList(sell_id,buy_type)
            addToCustomTaskList(task)


# 从生产者队列中删除元素
def removeProducerFromValueProducerList(worker_id):
    # 1,2,3类属于无限资源
    if worker_infos[worker_id][0] == 1 or worker_infos[worker_id][0] == 2 or worker_infos[worker_id][0] == 3:
        return

    if not producerIsExistInValueList(worker_id):
        return
    else:
        worker_type = worker_infos[worker_id][0]
        row = 0
        if worker_type == 1 or worker_type == 2 or worker_type == 3:
            row = 2
        elif worker_type == 4 or worker_type == 5 or worker_type == 6:
            row = 1
        elif worker_type == 7:
            row = 0
        value_producer_list[row].remove(worker_id)
        return


# 从消费者队列中删除元素
def removeConsumerFromConsumerList(sell_id,consume_type):
    #8类和9类属于无限消费资源
    if worker_infos[sell_id][0]==8 or worker_infos[sell_id][0]==9:
        return
    consumer_list[consume_type - 1].remove(sell_id)
    # for i in range(len(consumer_list[consume_type-1])):
    #     temp_sell_id = consumer_list[consume_type-1][i]
    #     if temp_sell_id == sell_id:
    #         consumer_list[consume_type - 1].remove(sell_id)
    #         return

def consumerIsExistInConsumerList(worker_id,consume_type):
    for i in range(len(consumer_list[consume_type-1])):
        temp_sell_id = consumer_list[consume_type-1][i]
        if temp_sell_id == worker_id:
            return True
    return False

# 判断目标worker_id是否存在于生产者队列者队列，即目标物品是否完成生产
def producerIsExistInValueList(worker_id):
    worker_type = worker_infos[worker_id][0]
    row = 0
    if worker_type == 1 or worker_type == 2 or worker_type == 3:
        row = 2
    elif worker_type == 4 or worker_type == 5 or worker_type == 6:
        row = 1
    elif worker_type == 7:
        row = 0
    for i in range(len(value_producer_list[row])):
        if value_producer_list[row][i] == worker_id:
            return True
    return False

# 目标任务是否存在于专属任务列中了
def taskIsExistInCustomTaskList(buy_id,sell_id):
    # print('buy_id=%d' % (buy_id),file=F)
    # print('sell_id=%d' % (sell_id), file=F)
    for i in range(4):
        for j in range(len(custom_task_list[i])):
            if custom_task_list[i][j][1] == buy_id and custom_task_list[i][j][2] == sell_id:
                return True
    return False

# 目标任务是否正在执行中
def taskIsInExecuting(buy_id,sell_id):
    for i in range(4):
        robot_phase = robot_task[i][0]
        if robot_phase != -1 and robot_task[i][1] == buy_id and robot_task[i][2] == sell_id:
            return True
    return False

# 判断worker_id是否持有worker_type类型的物品
def isHoldWorkerType(worker_id,product_type):
    worker_type = worker_infos[worker_id][0]
    holder = numConvertBinaryList(worker_infos[worker_id][4])[::-1]
    # 没有依赖关系自然不会有持有
    if depend_graph[product_type - 1][worker_type - 1] == 0:
        return False
    if depend_graph[product_type - 1][worker_type - 1] == 1 and holder[product_type] != '1':
        return False
    return True

# 找到离worker_id最近的类型为target_type的工作台
def findNearestWokerForType(worker_id,target_type):
    min_distance = 1000
    index = -1
    for i in range(worker_num):
        temp_type = worker_infos[i][0]
        distance = distance_graph[worker_id][i]
        if temp_type == target_type and distance < min_distance:
            min_distance = distance
            index = i
    return index

def printNode(node):
    for i in range(node.son_num):
        # print('%d号工作台的子节点为%d' %(node.id,node.sons[i].id), file=F)
        printNode(node.sons[i])

# 更新更合适的交付点
def updateExecutingTask(robot_id):
    sell_id = robot_task[robot_id][2]
    sell_type = worker_infos[sell_id][0] #当前在正执行任务的卖点
    buy_id = robot_task[robot_id][1]
    buy_type = worker_infos[buy_id][0]  # 当前在正执行任务的买点
    # 7类工作台的交付由外部控制，不随意更改
    if sell_type == 7:
        return

    min_weight_p2c = 999  # 机器人到购买点的最小权值
    new_sell_id = -1  # 卖点id，值为-1时视为未找到与买点适配的卖点
    min_consumer_type = getMinTypeOf456()  # 当前场上需要buy_type类型物品的工作台中，数量最少的类型
    # 根据找到的购买点为其寻找最合适的出售点
    for j in range(len(consumer_list[buy_type - 1])):
        temp_sell_id = consumer_list[buy_type - 1][j]  # 可用的卖点
        temp_sell_type = worker_infos[temp_sell_id][0]  # 卖点的类型
        distance_p2c = distance_graph[buy_id][temp_sell_id]  # 计算买点到可用卖点的距离
        holder_num = worker_infos[temp_sell_id][6]  # 目标销售点持有物品数量
        # 物品在运送途中的也被视为其拥有的
        for n in range(4):
            if robot_task[n][0] != -1 and robot_task[n][2] == temp_sell_id:
                holder_num = holder_num + 1
            for p in range(len(custom_task_list[n])):
                if custom_task_list[n][p][2] == temp_sell_id:
                    holder_num = holder_num + 1
        distance_c2center = calDistance(center[0], center[1], worker_infos[temp_sell_id][1], worker_infos[temp_sell_id][2])  # 计算可用卖点到中心点的距离
        # 计算中心点权值
        weight_p2c = distance_p2c * 1 + distance_c2center * 0.3 + (getNeedProductCount(temp_sell_type) - holder_num) * 10
        # 出于均衡，对于最少的类型我们提升其权重
        if min_consumer_type == temp_sell_type:
            weight_p2c = weight_p2c * 0.5
        if weight_p2c < min_weight_p2c:
            min_weight_p2c = weight_p2c
            new_sell_id = temp_sell_id
        # 最后1000帧开始判断任务是否可执行完，对于无法完成的任务不与更改
        if time > 8000 and (not canFinish(robot_id,buy_id,sell_id)):
            return
        # 未找到合适的售卖工作台
        if new_sell_id == -1:
            return
        else:
            holder_num = worker_infos[sell_id][6]  # 目标销售点持有物品数量
            # 物品在运送途中的也被视为其拥有的
            for n in range(4):
                if robot_task[n][0] != -1 and robot_task[n][2] == sell_id:
                    holder_num = holder_num + 1
                for p in range(len(custom_task_list[n])):
                    if custom_task_list[n][p][2] == sell_id:
                        holder_num = holder_num + 1
            #更改任务交付目标
            distance_c2center = calDistance(center[0], center[1], worker_infos[sell_id][1], worker_infos[sell_id][2])
            weight_p2c = distance_p2c * 1 + distance_c2center * 0.3 + (getNeedProductCount(sell_type) - holder_num) * 10
            if min_weight_p2c < weight_p2c:
                robot_task[robot_id][2] = new_sell_id
                removeConsumerFromConsumerList(new_sell_id,buy_type)
                consumer_list[buy_type].append(sell_id)
                return

    # distance_r2c = 0# 当前机器人执行完任务需要行走的距离
    # r_x = robot_infos[robot_id][7]# 机器人当前x坐标
    # r_y = robot_infos[robot_id][8]# 机器人当前y坐标
    # if robot_task[robot_id][0] == 0:
    #     distance_r2c = distance_graph[buy_id][sell_id]
    # elif robot_task[robot_id][0] == 1:
    #     sell_x = worker_infos[sell_id][1]
    #     sell_y = worker_infos[sell_id][2]
    #     distance_r2c = calDistance(r_x, r_y, sell_x, sell_y)
    # else:
    #     return
    #
    # for i in range(len(consumer_list[buy_type-1])):
    #     temp_sell_id = consumer_list[buy_type-1][i]#消费工作台的id
    #     temp_sell_type = worker_infos[temp_sell_id][0]#消费工作台的类型
    #     if temp_sell_type == sell_type:
    #         new_distance_r2c = 0
    #         if robot_task[robot_id][0] == 0:
    #             new_distance_r2c = distance_graph[buy_id][temp_sell_id]
    #         elif robot_task[robot_id][0] == 1:
    #             sell_x = worker_infos[temp_sell_id][1]
    #             sell_y = worker_infos[temp_sell_id][2]
    #             new_distance_r2c = calDistance(r_x, r_y, sell_x, sell_y)
    #         if new_distance_r2c < distance_r2c:
    #             print('变更%d机器人的目标，从原来的%d运送%d类物品到%d变为从%d运送%d类物品到%d变为' % (robot_id,buy_id,buy_type,sell_id,buy_id,buy_type,temp_sell_id),file=F)
    #             robot_task[robot_id][2] = temp_sell_id
    #             removeConsumerFromConsumerList(temp_sell_id, buy_type)
    #             consumer_list[buy_type-1].append(sell_id)
    #             return

class Node:

    def __init__(self, id, type,product_state):
        self.id = id # 工作台id
        self.type = type # 工作台类型
        self.product_state = product_state # 是否完成生产
        self.sons = [] # 所需材料对应的工作台节点
        self.son_num = 0

    def addSon(self, son):
        self.sons.append(son)
        self.son_num = self.son_num + 1

    def updateProductState(self,product_state):
        self.product_state = product_state  # 是否完成生产

if __name__ == '__main__':
    read_util_ok()
    finish()
    physics2 = Physics2.Physics()
    physics4 = Physics4.Physics()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.split(' ')
        # 读入帧数和金钱
        time = int(parts[0])
        money = int(parts[1])
        # print('------------------------------------------------------',file=F)
        # print(time,file=F)
        # 读入工作台状态信息和机器人信息
        updateInfo()
        # 初始化
        if flag == False:
            initInfo()
            flag = True
        read_util_ok()
        sys.stdout.write('%d\n' % time)
        if time > 8000 and haveSeven and worker_num == 18:
            root_node.id = -1
        # 更新机器人任务执行情况
        updateRobotTask()
        # print('消费者队列',file=F)
        # print(consumer_list,file=F)
        # print('生产者队列', file=F)
        # print(value_producer_list,file=F)
        # print('执行任务队列', file=F)
        # print(robot_task, file=F)
        # print('后备任务队列', file=F)
        # print(custom_task_list, file=F)
        # 分配任务
        assignTask()

        # 寻找可以顺路做的任务
        if worker_num == 25:
            for i in range(4):
                # 优先抢断顺路的主线任务
                if time > 0:
                    robExecutingTask(i)
                    generateTogetherTask2(i)
        elif worker_num == 18:
            for i in range(4):
                # 优先抢断顺路的主线任务
                if time < 8000:
                    robExecutingTask(i)
                    generateTogetherTask2(i)

        # 执行任务
        exec()

        finish()

