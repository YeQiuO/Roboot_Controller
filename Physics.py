import math
import sys

import Data


class Physics:
    # stop_distance = 1.2

    def __init__(self):
        self.is_close = [-1, -1, -1, -1]  # 1为已接近；-1为未接近
        self.target = [-1, -1, -1, -1]  # -1为初始化

    # 生成机器下一步行动的指令
    def doInstruct(self, robot_id, plat_id, speed, direction, robot_x, robot_y, target_id, target_x, target_y,
                   task_type, frame, task_start_type):

        if plat_id == target_id:  # 机器人所处位置 == 目标位置  and not (frame > 8500 and task_start_type == 7) and not frame > 8800
            if task_type == 0:
                sys.stdout.write('buy %d\n' % robot_id)
            if task_type == 1:
                sys.stdout.write('sell %d\n' % robot_id)

        Data.log_print(str(robot_id) + '正在前往' + str(target_x) + '，' + str(target_y) + '==' + str(task_type))

        # 计算前进方向和目标方向的夹角，angle>0目标方向与前进方向夹角的方向是顺时针方向
        angle = CalculateAngle(direction, target_x - robot_x, target_y - robot_y)

        if abs(angle) < abs(math.pi) / 50:
            # 当angle小于PI/50，开始降低转速
            angle_speed = 0
        else:
            # angle>PI/50顺时针旋转，angle<-PI/50逆时针旋转
            angle_speed = -math.pi if angle < 0 else math.pi

        distance = ((target_x - robot_x) ** 2 + (target_y - robot_y) ** 2) ** 0.5
        # 更新state、target
        old_target_robot = self.target[robot_id]
        self.target[robot_id] = target_id
        if distance < 2:
            self.is_close[robot_id] = 1
        if self.is_close[robot_id] == 1 and old_target_robot != self.target[robot_id]:
            self.is_close[robot_id] = -1

        # 速度定义
        angle_towards_destination = abs(angle) * 180 / math.pi
        if self.is_close[robot_id] == 1 and angle_towards_destination > 80:  # 开始绕圈
            line_speed = 0
        elif distance < 1.2:  # 到达目的地
            line_speed = 1.5 + distance / 1.2 * 0.5
        elif angle_towards_destination > 60:  # 角度过大
            # line_speed = 6 * ((180 - angle_towards_destination) / 120) ** 2
            line_speed = - (1/20) * angle_towards_destination + 9
        else:  # 对准了就冲吧
            line_speed = 6

        sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))


def CalculateAngle(direction, target_x, target_y):
    angle = math.atan2(target_y, target_x) - direction
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    return angle
