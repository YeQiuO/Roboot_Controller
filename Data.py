import math
import random
import sys

import numpy as np

from Current import Current
from Node import Node
from Robot import Robot
from Schedule import Schedule
from Task import Task
from Tree import Tree


def read_util_ok():
    while input() != "OK":
        pass


def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()


def log_print(log):
    return
    # mylog = open('recode.log', mode='a', encoding='utf-8')
    # print(log, file=mylog)
    # mylog.close()


def calDistance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** (0.5)


def loaner():
    return Task(Node(-2, -2, 0, 0, -2, -2, -2), Node(-2, -2, 0, 0, -2, -2, -2))


class Data:
    corresponding_material = [[], [], [], [], [2, 1], [3, 1], [3, 2]]

    fill_in = [0, 0, 0, 0, 6, 10, 12, 112, 0, 0]

    count_456 = 8
    distance_123 = 8

    def __init__(self):
        self.node_type = [[], [], [], [], [], [], [], [], [], []]
        self.node_ids = []
        self.robot = []
        self.node_count = 0
        self.frame = 1  # 帧数
        self.money = 20000  # 钱

        self.current_works = Current()
        self.schedule = Schedule()
        self.tree = None

        self.node_distance = None  # 父节点距离|x1-x2|+|y1-y2|排序

        self.stop_count = [0, 0, 0, 0]

        self.in_advance_to_get = [0, 0, 0, 0, 0, 0, 0, 200, 0, 0]
        self.in_advance_to_put = [0, 0, 0, 0, 50, 50, 50, 200, 0, 0]

    def load(self):
        # x = 0
        # y = 0
        # str_in = input()
        # while str_in != "OK":
        #     list_in = list(str_in)
        #     for i in range(len(list_in)):
        #         x = x + 0.5
        #         if list_in[i] == "A":  # 机器人起始位置
        #             self.robot.append([x, y])
        #         elif str.isdigit(list_in[i]):  # 工作台起始位置
        #             self.workbench[int(list_in[i]) - 1].append([x, y, -1, 0, 0])
        #     # 遍历
        #     x = 0
        #     y = y + 0.5
        #     str_in = input()
        #     pass
        while input() != "OK":
            pass
        # 结束
        finish()

    def update(self):

        # 输入
        self.node_type = [[], [], [], [], [], [], [], [], [], []]
        self.node_ids = []
        self.robot = []
        temp = sys.stdin.readline().split()
        while len(temp) == 0:
            temp = sys.stdin.readline().split()
        self.frame, self.money = int(temp[0]), int(temp[1])
        self.node_count = int(sys.stdin.readline().split()[0])
        for i in range(self.node_count):
            workbench = sys.stdin.readline().split()
            temp = Node(i, int(workbench[0]), float(workbench[1]), float(workbench[2]), int(workbench[3]),
                        int(workbench[4]), int(workbench[5]))
            self.node_type[temp.type].append(temp)
            self.node_ids.append(temp)
        for i in range(4):
            robot = sys.stdin.readline().split()
            temp = Robot(i, int(robot[0]), int(robot[1]), float(robot[2]), float(robot[3]), float(robot[4]),
                         float(robot[5]), float(robot[6]), float(robot[7]), float(robot[8]), float(robot[9]))
            self.robot.append(temp)

        # 初始化、更新树
        if self.frame == 1:
            # 计算距离矩阵
            self.node_distance = np.zeros((self.node_count, self.node_count))
            for i in range(self.node_count):
                for j in range(self.node_count):
                    self.node_distance[i][j] = calDistance(self.node_ids[i].x, self.node_ids[i].y, self.node_ids[j].x, self.node_ids[j].y)
            # 找到最优树结构
            self.tree = self.find_tree()
        else:
            # 更新 key_node
            if self.tree.pattern == 0:
                for i in range(len(self.tree.node)):
                    for j in range(len(self.tree.node[i])):
                        self.tree.node[i][j] = self.node_ids[self.tree.node[i][j].id]
            else:
                self.tree.node = self.node_ids[self.tree.node.id]

            # 更新 sons_node
            if self.tree.super_sons is not None:
                for i in range(len(self.tree.super_sons)):
                    id = self.tree.super_sons[i].id
                    self.tree.super_sons[i] = self.node_ids[id]
            if self.tree.sons is not None:
                for i in range(len(self.tree.sons)):
                    id = self.tree.sons[i].id
                    self.tree.sons[i] = self.node_ids[id]

        # 更新 拿到商品、任务完成
        for robot in self.robot:
            if self.current_works.list[robot.id] is not None:
                if self.current_works.list[robot.id].state == 0 and robot.thing_type != 0:
                    log_print(str(robot.id) + '拿到商品' + str(self.current_works.list[robot.id].start.type))
                    self.current_works.list[robot.id].state = 1

                elif self.current_works.list[robot.id].state == 1 and robot.thing_type == 0:
                    start = self.current_works.list[robot.id].start
                    # 结束预约
                    self.schedule.already_schedule_end_node_ids[start.type].remove(
                        self.current_works.list[robot.id].end.id)
                    if start.type in [4, 5, 6]:
                        self.schedule.already_schedule_start_node_ids.remove(start.id)

                    log_print(str(robot.id) + '任务完成' + str(self.current_works.list[robot.id].start.type))
                    self.current_works.wait += 1
                    self.current_works.list[robot.id] = None

        # 优先调度
        if self.tree.pattern == 0:

            # 优先调度：7生产 > 456生产
            self.priority_schedule(0)
            self.priority_schedule(1)

        elif self.tree.pattern == 1:

            # 优先调度：直系儿子生产
            for i in self.tree.sons:
                if self.try_consume_left(i, self.tree.node):
                    break

        # 次级调度：队空，456消费 入队列
        self.product_456()

        # 存在机器人未安排工作 且 队列不为空
        if self.current_works.wait != 0 and len(self.schedule.list) > 0:
            for i in range(len(self.current_works.list)):
                if self.current_works.list[i] is None and len(self.schedule.list) > 0:
                    task = self.schedule.get_task(self.robot[i].x, self.robot[i].y)

                    # 到达结束边缘临界
                    if self.frame > 8000 and not self.canFinish(task, self.robot[i].x, self.robot[i].y):
                        # 如果还有多余任务
                        self.product_456()
                        if len(self.schedule.list) > 0:
                            task = self.schedule.get_task(self.robot[i].x, self.robot[i].y)
                            if self.canFinish(task, self.robot[i].x, self.robot[i].y):
                                self.stop_count[self.robot[i].id] = 0
                            else:
                                task = None
                            self.stop_count[self.robot[i].id] += 1
                        else:
                            task = None
                        if self.stop_count[self.robot[i].id] == 3:
                            task = loaner()

                    self.current_works.list[i] = task
                    self.current_works.wait -= 1

        while input() != "OK":
            pass

    # 判断任务是否可以在结束前完成
    def canFinish(self, task, robot_x, robot_y):
        distance_b2s = calDistance(task.start.x, task.start.y, task.end.x, task.end.y)  # 买点和卖点的距离
        distance_r2b = calDistance(task.start.x, task.start.y, robot_x, robot_y)  # 机器人和买点的距离
        leave_time = (9000 - self.frame) / 50  # 计算剩余时间(秒)
        redundance = 2  # 冗余时间,增加容错
        avg_time = 4.5  # 平均行驶速度
        distance = distance_b2s + distance_r2b
        if (distance / avg_time + redundance) < leave_time:
            return True
        else:
            return False

    # in_produce：0，优先空闲的7
    def priority_schedule(self, in_produce):
        for node in self.tree.node:
            if len(self.tree.super_sons) > 0:
                for super_son in self.tree.super_sons:
                    # 未生产的工作台优先寻找产品
                    if in_produce == 0 and node[0].remain_time == -1:
                        self.try_consume_left(super_son, node[0])
                    # 然后考虑正在生产的工作台
                    elif in_produce == 1 and node[0].remain_time > 0:
                        self.try_consume_left(super_son, node[0])
            if len(self.tree.sons) > 0:
                for son in self.tree.sons:
                    # 未生产的工作台优先寻找产品
                    if in_produce == 0 and node[0].remain_time == -1:
                        self.try_consume_left(son, node[0])
                    # 然后考虑正在生产的工作台
                    elif in_produce == 1 and node[0].remain_time > 0:
                        self.try_consume_left(son, node[0])
            self.try_consume_left(node[0], node[1])

    def product_456(self):
        # need_count = self.schedule.size - len(self.schedule.list)
        if len(self.schedule.list) <= self.schedule.size:
            # 先调度super的节点
            if self.tree.super_sons is not None:
                for super_son in self.tree.super_sons:
                    for start_type in Data.corresponding_material[super_son.type]:
                        if self.have_location_to_put(super_son, start_type):
                            self.find_task(super_son, start_type)

            if self.tree.sons is not None:
                # 先调度未在生产中的节点
                for son in self.tree.sons:
                    for start_type in Data.corresponding_material[son.type]:
                        if son.remain_time == -1 and self.have_location_to_put(son, start_type):
                            self.find_task(son, start_type)
                # 再调度生产中的节点
                for son in self.tree.sons:
                    for start_type in Data.corresponding_material[son.type]:
                        if son.remain_time >= 0 and self.have_location_to_put(son, start_type):
                            self.find_task(son, start_type)

    def have_location_to_put(self, end, type):

        if self.schedule.already_schedule_end_node_ids[type].count(end.id) > 0:
            log_print('已经被预约，位置：' + str(type))
            return False

        # 判断是否有空位
        state = end.material_state
        for i in range(type):
            state /= 2
        state = math.floor(state)

        mua = False
        if end.material_state == Data.fill_in[end.type] and 0 < end.remain_time < self.in_advance_to_put[end.type]:
            mua = True

        return state % 2 == 0 or mua

    def consume(self, start, end, isleft):
        if isleft:
            self.schedule.left_insert(Task(start, end))
        else:
            self.schedule.right_insert(Task(start, end))

        if start.type in [4, 5, 6]:
            # 预约产品格
            self.schedule.already_schedule_start_node_ids.append(start.id)
        # 预约原材料格
        self.schedule.already_schedule_end_node_ids[start.type].append(end.id)

    def try_consume_left(self, start, end):
        if (start.product_state == 1 or (0 < start.remain_time < self.in_advance_to_get[start.type])) \
                and self.have_location_to_put(end, start.type) \
                and self.schedule.already_schedule_start_node_ids.count(start.id) == 0:
            self.consume(start, end, True)
            return True
        return False

    def try_consume_right(self, start, end):
        if start.product_state == 1 and self.have_location_to_put(end, start.type):
            self.consume(start, end, False)
            return True
        return False

    # 456有空位时，消费最近的123
    def find_task(self, end, type):

        if len(self.schedule.list) >= self.schedule.size:
            return

        # log_print("find_task"+str(end.type))
        temp = []
        for i in self.node_type[type]:
            temp.append([self.node_distance[i.id, end.id], i])
        temp = sorted(temp, key=lambda x: x[0])
        choice = temp[0][1]

        # 找最近的产品（123生产速度快，不考虑到达后未生产出产品的情况）PS:下面的方法，如果所有节点都在生产中，会出错
        # for i in temp:
        #     log_print(i)
        #     if i[1].product_state == 1:
        #         self.consume(i[1], end, False)

        # 如果该起点正被其他机器人选定，则换一个类似距离的节点
        # if len(temp) >= 2:
        #     start_ids = []
        #     for work in self.current_works.list:
        #         if work is not None:
        #             start_ids.append(work.start.id)
        #     if choice.id in start_ids and (self.node_distance[choice.id][end.id] - self.node_distance[temp[1][1].id][end.id]) < 10:
        #         choice = temp[1][1]

        self.consume(choice, end, False)

    def find_tree(self):
        temp = []
        distance = 0
        if len(self.node_type[7]) != 0:
            for i in self.node_type[7]:
                for j in self.node_type[8]:
                    temp.append([self.node_distance[i.id][j.id], i, j])
                for j in self.node_type[9]:
                    temp.append([self.node_distance[i.id][j.id], i, j])
            temp = sorted(temp, key=lambda x: x[0])
            if len(temp) == 1:
                node = [[temp[0][1], temp[0][2]]]
            else:
                node = [[temp[0][1], temp[0][2]], [temp[1][1], temp[1][2]]]
            sons = []
            super_sons = []
            sons_2 = []
            # 获取sons
            for key_node in node:
                for son_type in [6, 5, 4]:
                    temp = []
                    for i in self.node_type[son_type]:
                        temp.append([self.node_distance[i.id][key_node[0].id], i])
                    temp = sorted(temp, key=lambda x: x[0])
                    sons.append(temp[0][1])
                    # count(7)=1, 更新sons
                    if len(node) == 1:
                        if len(temp) >= 2:
                            sons_2.append(temp[1][1])
                            distance += self.node_distance[temp[1][1].id][key_node[0].id]
                        else:
                            sons.pop(len(sons) - 1)
                            super_sons.append(temp[0][1])
                    distance += self.node_distance[temp[0][1].id][key_node[0].id]

            distance = distance / (len(sons) + len(super_sons))
            self.in_advance_to_put[7] = (distance/4.5)*50-200

            # count(7)=2, 更新sons，去重
            if len(node) == 2:
                temp = []
                for son in sons:
                    if son not in temp:
                        temp.append(son)
                    else:
                        temp.remove(son)
                        if son not in super_sons:
                            super_sons.append(son)
                sons = temp
                #
                # for son in sons:
                #     distance += self.node_distance(son.id)
                # for son in super_sons:
                #     distance += self.node_distance(son.id)
            else:
                sons.extend(sons_2)

            tree = Tree(node, 0)
            tree.update_0(super_sons, sons)
        else:
            son = self.node_type[4]
            son.extend(self.node_type[5])
            son.extend(self.node_type[6])
            for i in self.node_type[9]:
                sum = 0
                for j in son:
                    sum += self.node_distance[i.id][j.id]
                temp.append([sum, i])
            log_print(temp)
            temp = sorted(temp, key=lambda x: x[0])
            key_node = temp[0][1]
            temp = []
            for i in [4, 5, 6]:
                for j in self.node_type[i]:
                    temp.append([self.node_distance[key_node.id][j.id], j])
            temp = sorted(temp, key=lambda x: x[0])
            length = int(len(temp) / 2) + 1 if int(len(temp) / 2) + 1 >= Data.count_456 else len(temp)
            sons = []
            for i in temp[:length]:
                sons.append(i[1])
            for i in [1, 2, 3]:
                for j in self.node_type[i]:
                    if self.node_distance[key_node.id][j.id] < Data.distance_123:
                        sons.append(j)

            tree = Tree(key_node, 1)
            tree.update_1(sons)
        return tree
