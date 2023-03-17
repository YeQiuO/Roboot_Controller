import numpy as np

import Data


class Schedule:

    # 双端队列
    def __init__(self):
        self.list = []
        self.already_schedule_start_node_ids = []
        self.already_schedule_end_node_ids = [[], [], [], [], [], [], [], [], [], []]

        self.size = 2

    def left_insert(self, task):
        self.list.insert(0, task)

    def right_insert(self, task):
        self.list.append(task)

    def get_task(self, robot_x, robot_y):
        distance = []
        for i in range(len(self.list)):
            start = self.list[i].start
            distance.append([abs(robot_x - start.x) + abs(robot_y - start.y), i])
        temp = sorted(distance, key=lambda x: x[0])
        # Data.log_print("distance"+str(self.list[temp[0][1]].start.type))

        return self.list.pop(temp[0][1])
