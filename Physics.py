import math
import sys

import Data


class Physics:
    stop_distance = 2

    def __init__(self):
        self.is_close = [-1, -1, -1, -1]  # 1为已接近；-1为未接近
        self.target = [-1, -1, -1, -1]  # -1为初始化

    # 生成机器下一步行动的指令
    def doInstruct(self, robot_id, plat_id, speed, direction, robot_x, robot_y, target_id, target_x, target_y,
                   task_type,
                   frame, task_end_type):

        if plat_id == target_id:  # 机器人所处位置 == 目标位置
            if task_type == 0 and not (frame > 8500 and task_end_type == 8):
                sys.stdout.write('buy %d\n' % robot_id)
            if task_type == 1:
                sys.stdout.write('sell %d\n' % robot_id)

        Data.log_print(str(robot_id) + '正在前往' + str(target_x) + '，' + str(target_y) + '==' + str(task_type))

        # 计算前进方向和目标方向的夹角，angle>0目标方向与前进方向夹角的方向是顺时针方向
        z1 = target_x - robot_x
        z2 = target_y - robot_y
        angle = math.atan2(z2, z1) - direction
        if angle > math.pi:
            angle -= 2 * math.pi
        if angle < -math.pi:
            angle += 2 * math.pi

        if abs(angle) < abs(math.pi) / 50:
            # 当angle小于PI/50，开始降低转速
            angle_speed = 0
        else:
            # angle>PI/50顺时针旋转，angle<-PI/50逆时针旋转
            angle_speed = -math.pi if angle < 0 else math.pi

        distance = (z1 ** 2 + z2 ** 2) ** 0.5
        # 更新state、target
        old_target_robot = self.target[robot_id]
        self.target[robot_id] = target_id
        if distance < 2:
            self.is_close[robot_id] = 1
        if self.is_close[robot_id] == 1 and old_target_robot != self.target[robot_id]:
            self.is_close[robot_id] = -1

        # 速度定义
        # speed = 2 if (distance < 1.2) or abs(angle-math.pi/2) < 10 else 6
        speed = 6
        if self.is_close[robot_id] == 1 and abs(angle) * 180 / math.pi > 80:
            speed = 0
        elif distance < 1.2:
            speed = 1.5 + distance / 1.2 * 0.5
        elif abs(angle) * 180 / math.pi > 160:
            speed = 2
        elif abs(angle) * 180 / math.pi > 140:
            speed = 3
        elif abs(angle) * 180 / math.pi > 120:
            speed = 4

        # 接近左边墙并且朝向和左边墙的法向量大于90°，说明会撞墙，要减速转头
        if robot_x < Physics.stop_distance and abs(CalculateAngle(direction, 1, 0)) >= math.pi / 1.895:
            speed = 1
        # 接近右边墙并且朝向和右边墙边墙的法向量大于90°，说明会撞墙，要减速转头
        if robot_x > 50 - Physics.stop_distance and abs(CalculateAngle(direction, -1, 0)) >= math.pi / 1.895:
            speed = 1
        if robot_y < Physics.stop_distance and abs(CalculateAngle(direction, 0, 1)) >= math.pi / 1.895:
            speed = 1
        if robot_y > 50 - Physics.stop_distance and abs(CalculateAngle(direction, 0, -1)) >= math.pi / 1.895:
            speed = 1

        sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        sys.stdout.write('forward %d %d\n' % (robot_id, speed))


def CalculateAngle(direction: object, target_x: object, target_y: object) -> object:
    angle = math.atan2(target_y, target_x) - direction
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    return angle