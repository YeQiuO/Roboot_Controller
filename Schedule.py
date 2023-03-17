import numpy as np

import Data


class Schedule:
    size = 3

    # 双端队列
    def __init__(self):
        self.list = []
        self.already_schedule_start_node_ids = []
        self.already_schedule_end_node_ids = [[], [], [], [], [], [], [], [], [], []]

    def left_insert(self, task):
        self.list.insert(0, task)

    def right_insert(self, task):
        self.list.append(task)

    def get_task(self, start_x, start_y):
        distance = []
        for i in range(len(self.list)):
            Data.log_print(self.list[i].start.type)
            start = self.list[i].start
            distance.append([np.abs(start_x - start.x) + np.abs(start_y - start.y), i])
        temp = sorted(distance, key=lambda x: x[0])
        # Data.log_print("distance"+str(self.list[temp[0][1]].start.type))

        return self.list.pop(temp[0][1])
