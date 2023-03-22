import numpy as np

import Data


class Schedule:

    # 双端队列
    def __init__(self):
        self.list = []
        # 预约产品格
        self.already_schedule_start_node_ids = []
        # 预约原材料格
        self.already_schedule_end_node_ids = [[], [], [], [], [], [], [], [], [], []]

        self.size = 2

    def left_insert(self, task):
        self.list.insert(0, task)

    def right_insert(self, task):
        self.list.append(task)

    def get_task(self, robot_id, robots, current_works, frame):
        if len(self.list) == 0:
            return current_works

        # 抢断
        task = self.list[self.find_nearest_task_index(robots[robot_id].x, robots[robot_id].y)]
        closest = Data.calDistance(robots[robot_id].x, robots[robot_id].y, task.start.x, task.start.y)
        closest_id = -1
        for i in range(4):
            if robot_id == i or current_works.list[i] is None or current_works.list[i].state == 1:
                continue

            node = current_works.list[i].start
            if Data.calDistance(robots[robot_id].x, robots[robot_id].y, node.x, node.y) < Data.calDistance(robots[i].x, robots[i].y, node.x, node.y) < closest:
                closest = Data.calDistance(robots[i].x, robots[i].y, node.x, node.y)
                closest_id = i

        if closest_id == -1:
            current_works.list[robot_id] = self.give_task(robots[robot_id].x, robots[robot_id].y, frame)
        else:
            current_works.list[robot_id] = current_works.list[closest_id]
            current_works.list[closest_id] = self.give_task(robots[closest_id].x, robots[closest_id].y, frame)

        # 返回整体
        count = 0
        for i in current_works.list:
            if i is None:
                count += 1
        current_works.wait = count

        return current_works

    def give_task(self, robot_x, robot_y, frame):
        if len(self.list) == 0:
            return None

        index = self.find_nearest_task_index(robot_x, robot_y)

        # 防止时间不够导致任务无法完成
        if index == -1 or not canFinish(self.list[index], robot_x, robot_y, frame):
            return None
        else:
            return self.list.pop(index)

    def find_nearest_task_index(self, robot_x, robot_y):
        distance = []
        for i in range(len(self.list)):
            start = self.list[i].start
            distance.append([abs(robot_x - start.x) + abs(robot_y - start.y), i])
        temp = sorted(distance, key=lambda x: x[0])
        return temp[0][1] if len(temp) > 0 else -1


# 判断任务是否可以在结束前完成
def canFinish(task, robot_x, robot_y, frame):
    distance_b2s = Data.calDistance(task.start.x, task.start.y, task.end.x, task.end.y)  # 买点和卖点的距离
    distance_r2b = Data.calDistance(task.start.x, task.start.y, robot_x, robot_y)  # 机器人和买点的距离
    leave_time = (9000 - frame) / 50  # 计算剩余时间(秒)
    redundance = 2  # 冗余时间,增加容错
    avg_time = 4.5  # 平均行驶速度
    distance = distance_b2s + distance_r2b
    if (distance / avg_time + redundance) < leave_time:
        return True
    else:
        return False
