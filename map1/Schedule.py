import numpy as np
from map1 import Data
from map1.Task import Task


class Schedule:

    # 双端队列 改 两层优先级list
    def __init__(self):

        self.priority_1 = []
        self.priority_2 = []
        self.priority_3 = []

        self.size_3 = 4

        self.weight_1 = 0.5
        self.weight_2 = 1.5
        self.weight_3 = 3

        # 预约产品格【仅仅预约4567的产品】
        self.already_schedule_start_node_ids = []
        # 预约原材料格
        self.already_schedule_end_node_ids = [[], [], [], [], [], [], [], [], [], []]

        self.node_distance = []

    def insert_priority_1(self, task):
        self.priority_1.append(task)

    def insert_priority_2(self, task):
        self.priority_2.append(task)

    def insert_priority_3(self, task):
        self.priority_3.append(task)

    def get_task(self, robot_id, robots, current_works, frame, node_type):
        if len(self.priority_1) == 0 and len(self.priority_2) == 0 and len(self.priority_3) == 0:
            return current_works

        # 抢断
        task = self.find_shortest_path_task(robots[robot_id].x, robots[robot_id].y, node_type, current_works, frame)
        closest = Data.calDistance(robots[robot_id].x, robots[robot_id].y, task.start.x, task.start.y)
        closest_id = -1
        for i in range(4):
            if robot_id == i or current_works.list[i] is None or current_works.list[i].state == 1:
                continue

            node = current_works.list[i].start
            temp = Data.calDistance(robots[i].x, robots[i].y, node.x, node.y)
            if Data.calDistance(robots[robot_id].x, robots[robot_id].y, node.x, node.y) < temp < closest:
                closest = temp
                closest_id = i

        if closest_id == -1:
            current_works.list[robot_id] = self.pop_task(task, frame, robots[robot_id].x, robots[robot_id].y)
        else:
            current_works.list[robot_id] = current_works.list[closest_id]
            current_works.list[closest_id] = None

        # 返回整体
        count = 0
        for i in current_works.list:
            if i is None:
                count += 1
        current_works.wait = count

        return current_works if closest_id == -1 else self.get_task(closest_id, robots, current_works, frame, node_type)

    def pop_task(self, task, frame, robot_x, robot_y):

        # 防止时间不够导致任务无法完成
        if canFinish(task, robot_x, robot_y, frame):
            for priority in [self.priority_1, self.priority_2, self.priority_3]:
                for index in range(len(priority)):
                    temp_task = priority[index]
                    start = temp_task.start
                    end = temp_task.end
                    if task.start.id == start.id and task.end.id == end.id:
                        return priority.pop(index)
        else:
            return None

    def find_shortest_path_task(self, robot_x, robot_y, node_type, current_works, frame):
        distance = []
        for priority in [[self.priority_1, self.weight_1], [self.priority_2, self.weight_2], [self.priority_3, self.weight_3]]:
            for task in priority[0]:
                start = task.start
                end = task.end
                distance.append([(Data.calDistance(robot_x, robot_y, start.x, start.y) + self.node_distance[start.id][end.id]) * priority[1], task])
        temp = sorted(distance, key=lambda x: x[0])

        # 如果起始位置已经被作为终点，则舍弃【目的：避免快到之后任务被抢了，也给前往该点机器人多一个任务】
        shortest_path_task = None
        for task in temp:
            task = task[1]
            is_same = False
            for current in current_works.list:
                if current is not None and current.state == 1 and task.start.id == current.end.id and not (task.end.type==8 and frame > 8000):
                    is_same = True
            if not is_same:
                shortest_path_task = task
                break
        shortest_path_task = temp[0][1] if shortest_path_task is None else shortest_path_task  # [会出bug]

        # 按照当前位置更新起点
        start = shortest_path_task.start
        end = shortest_path_task.end
        # 距离：机器人到起点+起点到终点
        robot_to_start_length = Data.calDistance(robot_x, robot_y, start.x, start.y) + self.node_distance[start.id][end.id]
        # 寻找更优起始点
        shortest_distance = robot_to_start_length
        better_node = None
        for node in node_type[start.type]:
            if node.id == start.id or node.product_state == 0:
                continue
            temp = Data.calDistance(robot_x, robot_y, node.x, node.y) + self.node_distance[node.id][end.id]
            if temp < shortest_distance:
                better_node = node
                shortest_distance = temp
        # 如果找到更优起始结点 替代
        if better_node is not None and self.already_schedule_start_node_ids.count(better_node.id) == 0:
            if start.type in [4, 5, 6, 7]:
                self.already_schedule_start_node_ids.remove(start.id)
                self.already_schedule_start_node_ids.append(better_node.id)

            self.update_task(shortest_path_task, Task(better_node, end))

        return Task(better_node, end) if better_node is not None else shortest_path_task

    def update_task(self, old_task, new_task):
        for priority in [self.priority_1, self.priority_2, self.priority_3]:
            for index in range(len(priority)):
                task = priority[index]
                start = task.start
                end = task.end
                if old_task.start.id == start.id and old_task.end.id == end.id:
                    priority[index] = new_task

    # 同类型存在更近距离的节点，只是该节点暂时未入队列
    # def find_better_task(self, robot_x, robot_y, start_x, start_y, start_type):
    #     distance = []
    #     for i in range(len(self.list)):
    #         start = self.list[i].start
    #         distance.append([abs(robot_x - start.x) + abs(robot_y - start.y), i])
    #     temp = sorted(distance, key=lambda x: x[0])
    #     return temp[0][1] if len(temp) > 0 else -1


# 判断任务是否可以在结束前完成
def canFinish(task, robot_x, robot_y, frame):
    distance_b2s = Data.calDistance_precise(task.start.x, task.start.y, task.end.x, task.end.y)  # 买点和卖点的距离
    distance_r2b = Data.calDistance_precise(task.start.x, task.start.y, robot_x, robot_y)  # 机器人和买点的距离
    distance = distance_b2s + distance_r2b
    leave_time = (9000 - frame) / 50  # 计算剩余时间(秒)
    redundance = 2  # 冗余时间,增加容错
    avg_time = 6  # 平均行驶速度
    if task.start.type in [4, 5, 6]:
        return True
    if (distance / avg_time + redundance) < leave_time:
        return True
    else:
        return False
