import math
import random
import sys

import numpy as np

from map3.Current import Current
from map3.Node import Node
from map3.Robot import Robot
from map3.Schedule import Schedule
from map3.Task import Task
from map3.Tree import Tree


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
    return abs(x2 - x1) + abs(y2 - y1)


def calDistance_precise(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def loaner():
    return Task(Node(-2, -2, 0, 0, -2, -2, -2), Node(-2, -2, 0, 0, -2, -2, -2))


# 判断是否有空位
def have_space(state, type):
    for i in range(type):
        state /= 2
    state = math.floor(state)
    return state % 2 == 0


class Data:
    corresponding_material = [[], [], [], [], [2, 1], [3, 1], [3, 2]]

    fill_in = [0, 0, 0, 0, 6, 10, 12, 112, 0, 0]

    count_456 = 7
    distance_123 = 9

    average_position = [[0, 0], [0, 0], [0, 0], [0, 0]]

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

        self.in_advance_to_get = [0, 0, 0, 0, 75, 75, 75, 150, 0, 0]
        self.in_advance_to_put = [0, 0, 0, 0, 50, 50, 50, 200, 0, 0]

    def load(self):

        _in = input()
        count = 0
        while _in != "OK":
            aaa = list(_in)
            for i in aaa:
                if i.isdigit():
                    count += 1
            _in = input()
        # 结束
        finish()
        return count

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
            log_print("temp:" + str(temp.id) + "," + str(temp.x) + "," + str(temp.y) + "," + str(temp.type))
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
                    self.node_distance[i][j] = calDistance(self.node_ids[i].x, self.node_ids[i].y, self.node_ids[j].x,
                                                           self.node_ids[j].y)
            self.schedule.node_distance = self.node_distance
            # 找到最优树结构
            self.tree = self.find_tree()

            for index in range(4):
                self.average_position[index][0] = self.robot[index].x
                self.average_position[index][1] = self.robot[index].y

        else:
            # 更新 key_node
            if self.tree.pattern == 0:
                # 调整 sons super_sons
                for i in range(len(self.tree.node)):
                    self.tree.node[i][0] = self.node_ids[self.tree.node[i][0].id]  # 7
                    self.tree.node[i][1] = self.node_ids[self.tree.node[i][1].id]  # 8/9

                    material_state = self.tree.node[i][0].material_state
                    vacancy_count_4 = 1 if have_space(material_state, 4) else 0
                    vacancy_count_5 = 1 if have_space(material_state, 5) else 0
                    vacancy_count_6 = 1 if have_space(material_state, 6) else 0

                    # 出现不均衡现象
                    if vacancy_count_4 + vacancy_count_5 + vacancy_count_6 == 1:
                        if vacancy_count_4 == 1:
                            self.tree.insert_super_son(self.find_nearest_son(self.tree.node[i][0].id, 4),
                                                       self.tree.node[i][0].id, self.node_ids)
                        if vacancy_count_5 == 1:
                            self.tree.insert_super_son(self.find_nearest_son(self.tree.node[i][0].id, 5),
                                                       self.tree.node[i][0].id, self.node_ids)
                        if vacancy_count_6 == 1:
                            self.tree.insert_super_son(self.find_nearest_son(self.tree.node[i][0].id, 6),
                                                       self.tree.node[i][0].id, self.node_ids)

                    # 更新 判断不均衡现象是否消失
                    self.tree.update_super_son(self.tree.node[i][0].id,
                                               [vacancy_count_4, vacancy_count_5, vacancy_count_6], self.node_ids)

            else:
                self.tree.node = self.node_ids[self.tree.node.id]  # 9

            # 更新 sons_node
            for sons in [self.tree.super_sons, self.tree.sons, self.tree.grand_son]:
                for i in range(len(sons)):
                    id = sons[i].id
                    sons[i] = self.node_ids[id]

        # 更新平均位置
        if self.frame % 50 == 0:
            for index in range(len(self.robot)):
                self.average_position[index][0] *= 0.8
                self.average_position[index][0] += self.robot[index].x * 0.2
                self.average_position[index][1] *= 0.8
                self.average_position[index][1] += self.robot[index].y * 0.2

        # 更新机器人信息
        for robot in self.robot:
            if self.current_works.list[robot.id] is not None:

                # 更新距离
                if self.current_works.list[robot.id].state == 0:
                    self.current_works.remain_distance[robot.id] = \
                        calDistance_precise(robot.x, robot.y, self.current_works.list[robot.id].start.x,
                                            self.current_works.list[robot.id].start.y)
                else:
                    self.current_works.remain_distance[robot.id] = \
                        calDistance_precise(robot.x, robot.y, self.current_works.list[robot.id].end.x,
                                            self.current_works.list[robot.id].end.y)

                # 更新拿到商品
                if self.current_works.list[robot.id].state == 0 and robot.thing_type != 0:
                    log_print(str(robot.id) + '拿到商品' + str(self.current_works.list[robot.id].start.type))
                    self.current_works.list[robot.id].state = 1

                # 更新任务完成
                elif self.current_works.list[robot.id].state == 1 and robot.thing_type == 0:
                    start = self.current_works.list[robot.id].start
                    end = self.current_works.list[robot.id].end
                    # 结束预约
                    if self.frame < 8597:
                        if end.type not in [8, 9]:
                            self.schedule.already_schedule_end_node_ids[start.type].remove(end.id)
                        if start.type in [4, 5, 6, 7]:
                            self.schedule.already_schedule_start_node_ids.remove(start.id)

                    log_print(str(robot.id) + '任务完成' + str(start.type))
                    self.current_works.wait += 1
                    self.current_works.list[robot.id] = None

        # 其余约束
        if self.frame == 8500:
            self.in_advance_to_get[7] = 400

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
        if self.current_works.wait != 0:
            for i in range(len(self.current_works.list)):
                if self.current_works.list[i] is None:
                    self.current_works = self.schedule.get_task(i, self.robot, self.current_works, self.frame,
                                                                self.node_type)

        while input() != "OK":
            pass

    # in_produce：0，优先空闲的7
    def priority_schedule(self, in_produce):
        # 给7节点排序，剩余运行时间短的在前
        order = []
        for node in self.tree.node:
            order.append([node[0].remain_time, node])
        order = sorted(order, key=lambda x: x[0])
        order = [x[1] for x in order]

        for node in order:
            # log_print("==7"+","+str(node[0].x)+","+str(node[0].y))
            for super_son in self.tree.super_sons:
                # 未生产的工作台优先寻找产品
                if in_produce == 0 and node[0].remain_time == -1:
                    self.try_consume_left(super_son, node[0])
                # 然后考虑正在生产的工作台
                elif in_produce == 1 and node[0].remain_time > 0:
                    self.try_consume_left(super_son, node[0])
            for son in self.tree.sons:
                # 未生产的工作台优先寻找产品
                if in_produce == 0 and node[0].remain_time == -1:
                    self.try_consume_left(son, node[0])
                # 然后考虑正在生产的工作台
                elif in_produce == 1 and node[0].remain_time > 0:
                    self.try_consume_left(son, node[0])
            self.try_consume_left(node[0], node[1])

    def product_456(self):
        if self.frame < 5:
            for son in self.tree.grand_son:
                for start_type in Data.corresponding_material[son.type]:
                    if self.have_location_to_put(son, start_type):
                        self.find_task(son, start_type)

        if len(self.schedule.priority_3) <= self.schedule.size_3:
            # 调度未在生产中的sons节点
            for sons in [self.tree.super_sons, self.tree.sons]:
                for son in sons:
                    for start_type in Data.corresponding_material[son.type]:
                        if son.remain_time == -1 and self.have_location_to_put(son, start_type):
                            self.find_task(son, start_type)
                            if len(self.schedule.priority_3) <= self.schedule.size_3:
                                return
            # 调度正在生产中的sons节点
            for sons in [self.tree.super_sons, self.tree.sons]:
                for son in sons:
                    for start_type in Data.corresponding_material[son.type]:
                        if son.remain_time >= 0 and self.have_location_to_put(son, start_type):
                            self.find_task(son, start_type)
                            if len(self.schedule.priority_3) <= self.schedule.size_3:
                                return

            for son in self.tree.grand_son:
                for start_type in Data.corresponding_material[son.type]:
                    if self.have_location_to_put(son, start_type):
                        self.find_task(son, start_type)

    def have_location_to_put(self, end, type):

        if self.schedule.already_schedule_end_node_ids[type].count(end.id) > 0:
            # log_print('已经被预约，位置：' + str(type))
            return False

        # 暂无位置 但即将有位置
        mua = False
        if end.material_state == Data.fill_in[end.type] and 0 < end.remain_time < self.in_advance_to_put[
            end.type] and end.product_state == 0:
            mua = True

        return have_space(end.material_state, type) or mua

    def consume(self, start, end):
        if start.type in [7] or (self.frame < 7000 and (
                (end in self.tree.super_sons and end.product_state == 0) or (start in self.tree.super_sons))):
            self.schedule.insert_priority_1(Task(start, end))
            # 预约产品格
            self.schedule.already_schedule_start_node_ids.append(start.id)
        elif start.type in [4, 5, 6]:
            self.schedule.insert_priority_2(Task(start, end))
            # 预约产品格
            self.schedule.already_schedule_start_node_ids.append(start.id)
        elif start.type in [1, 2, 3]:
            self.schedule.insert_priority_3(Task(start, end))

        if end.type not in [8, 9]:
            # 预约原材料格
            self.schedule.already_schedule_end_node_ids[start.type].append(end.id)

    def try_consume_left(self, start, end):
        if (start.product_state == 1 or (0 < start.remain_time < self.in_advance_to_get[start.type])) \
                and self.have_location_to_put(end, start.type) \
                and self.schedule.already_schedule_start_node_ids.count(start.id) == 0:
            self.consume(start, end)
            return True
        return False

    def try_consume_right(self, start, end):
        if start.product_state == 1 and self.have_location_to_put(end, start.type):
            self.consume(start, end)
            return True
        return False

    def change_order(self, order):
        sons = []
        super_sons = []
        for i in order:
            for son in self.tree.sons:
                if son.type == i:
                    sons.append(son)
            for super_son in self.tree.super_sons:
                if super_son.type == i:
                    super_sons.append(super_son)
        self.tree.sons = sons
        self.tree.super_sons = super_sons

    # 456有空位时，消费最近的123
    def find_task(self, end, type):

        # 计算平均位置
        average_x = 0
        average_y = 0
        for i in self.average_position:
            average_x += i[0]
            average_y += i[1]
        average_x /= 4
        average_y /= 4

        # 计算start节点和平均位置的距离+start和end节点的距离排序
        temp = []
        for i in self.node_type[type]:
            temp.append([self.node_distance[i.id, end.id] + calDistance(i.x, i.y, average_x, average_y), i])
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
        #     if choice.id in start_ids and (self.node_distance[choice.id][end.id] - self.node_distance[temp[1][1].id][end.id]) < 3:
        #         choice = temp[1][1]

        self.consume(choice, end)

    def find_tree(self):
        temp = []
        if len(self.node_ids) == 43:
            self.in_advance_to_get[7] = 50
            node = [[self.node_ids[21], self.node_ids[14]], [self.node_ids[12], self.node_ids[6]]]
            # tree.update_0([self.node_ids[38], self.node_ids[13], self.node_ids[29]])

            sons = []
            # 获取sons\最短路径
            min_length = 9999
            min_start = -1
            min_end = -1
            for key_node in node:
                for son_type in [6, 5, 4]:
                    temp = []
                    for i in self.node_type[son_type]:
                        temp.append([self.node_distance[i.id][key_node[0].id], i])
                    temp = sorted(temp, key=lambda x: x[0])
                    sons.append(temp[0][1])
                    min_distance = temp[0][0]
                    if min_distance < min_length:
                        min_length = min_distance
                        min_start = temp[0][1].id
                        min_end = key_node[0].id
                    # if len(node) > 1:
                    #     for son in temp:
                    #         distance = son[0]
                    #         son = son[1]
                    #         if distance - min_distance < 5:
                    #             sons.append(son)
                    if len(node) == 1 and len(temp) > 1:
                        # sons.append(temp[1][1])
                        for son in temp:
                            distance = son[0]
                            son = son[1]
                            if distance - min_distance < 5:
                                sons.append(son)

            self.in_advance_to_put[7] = (calDistance_precise(self.node_ids[min_start].x, self.node_ids[min_start].y,
                                                             self.node_ids[min_end].x,
                                                             self.node_ids[min_end].y) / 4.5) * 50

            # 去重
            temp = []
            for son in sons:
                if son not in temp:
                    temp.append(son)
            sons = temp
            tree = Tree(node, 0)
            tree.update_0(sons)

        elif len(self.node_type[7]) != 0:
            for i in self.node_type[7]:
                for j in self.node_type[8]:
                    temp.append([self.node_distance[i.id][j.id], i, j])
                for j in self.node_type[9]:
                    temp.append([self.node_distance[i.id][j.id], i, j])
            temp = sorted(temp, key=lambda x: x[0])
            # 取距离最近的两个7

            node = [[temp[0][1], temp[0][2]]]
            for i in range(len(temp)):
                if temp[i][1] != temp[0][1]:
                    node.append([temp[i][1], temp[i][2]])
                    break
            sons = []
            # 获取sons\最短路径
            min_length = 9999
            min_start = -1
            min_end = -1
            for key_node in node:
                for son_type in [6, 5, 4]:
                    temp = []
                    for i in self.node_type[son_type]:
                        temp.append([self.node_distance[i.id][key_node[0].id], i])
                    temp = sorted(temp, key=lambda x: x[0])
                    sons.append(temp[0][1])
                    min_distance = temp[0][0]
                    if min_distance < min_length:
                        min_length = min_distance
                        min_start = temp[0][1].id
                        min_end = key_node[0].id
                    # if len(node) > 1:
                    #     for son in temp:
                    #         distance = son[0]
                    #         son = son[1]
                    #         if distance - min_distance < 5:
                    #             sons.append(son)
                    if len(node) == 1 and len(temp) > 1:
                        # sons.append(temp[1][1])
                        for son in temp:
                            distance = son[0]
                            son = son[1]
                            if distance - min_distance < 5:
                                sons.append(son)

            self.in_advance_to_put[7] = (calDistance_precise(self.node_ids[min_start].x, self.node_ids[min_start].y,
                                                             self.node_ids[min_end].x,
                                                             self.node_ids[min_end].y) / 4.5) * 50

            # 去重
            temp = []
            for son in sons:
                if son not in temp:
                    temp.append(son)
            sons = temp

            tree = Tree(node, 0)
            tree.update_0(sons)

        else:
            sons_temp = []
            sons_temp.extend(self.node_type[6])
            sons_temp.extend(self.node_type[5])
            sons_temp.extend(self.node_type[4])
            for i in self.node_type[9]:
                sum = 0
                for j in sons_temp:
                    sum += self.node_distance[i.id][j.id]
                temp.append([sum, i])
            temp = sorted(temp, key=lambda x: x[0])
            key_node = temp[0][1]

            temp = []
            for j in sons_temp:
                temp.append([self.node_distance[key_node.id][j.id], j])
            temp = sorted(temp, key=lambda x: x[0])
            # length = int(len(temp) / 2) + 1 if int(len(temp) / 2) + 1 >= Data.count_456 else len(temp)
            length = Data.count_456 if len(temp) > Data.count_456 else len(temp)
            sons = []
            # 插入距离进的 Data.count_456 个456
            for i in temp[:length]:
                sons.append(i[1])
            # 插入距离进 Data.distance_123 个123
            for i in [1, 2, 3]:
                for j in self.node_type[i]:
                    if self.node_distance[key_node.id][j.id] < Data.distance_123:
                        sons.append(j)
            # 选择距离类似的5个节点作为grand_son
            grand_sons = []
            # length_2 = Data.count_456*2 if len(temp) > Data.count_456*2 else len(temp)
            # for i in temp[length:length_2]:
            #     grand_sons.append(i[1])
            # 在其余节点中选择距离原材料近的作为grand_son
            for node in sons_temp:
                if node not in sons and node not in grand_sons:
                    quits = False
                    for material_type in Data.corresponding_material[node.type]:
                        for node_123 in self.node_type[material_type]:
                            if calDistance(node_123.x, node_123.y, node.x, node.y) < Data.distance_123:
                                grand_sons.append(node)
                                quits = True
                                break
                        if quits:
                            break

            tree = Tree(key_node, 1)
            tree.update_1(sons, grand_sons)

            self.schedule.size_3 = 16
            self.schedule.weight_3 = 2
            # self.schedule.weight_2 = 1

        return tree

    def find_nearest_son(self, key_node_id, son_type):
        son_id = -1
        min_distance = 999
        for son in self.tree.sons:
            if son.type == son_type and self.node_distance[key_node_id][son.id] < min_distance:
                min_distance = self.node_distance[key_node_id][son.id]
                son_id = son.id
        return son_id
