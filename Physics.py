import math
import sys

import numpy as np

import Data

critical_change = 2 * math.pi


class Physics:

    def __init__(self):
        self.is_close = [-1, -1, -1, -1]  # 1为已接近；-1为未接近
        self.target = [-1, -1, -1, -1]  # -1为初始化

        self.sustain = [0, 0, 0, 0]
        self.sustain_line_speed = [0, 0, 0, 0]
        self.sustain_angle_speed = [0, 0, 0, 0]

        self.robots_toward_to_line = []

    # 生成机器下一步行动的指令
    def doInstruct(self, robot_id, plat_id, robot_direction, robot_x, robot_y, robot_angle_speed, robot_speed_x, robot_speed_y, target_id, target_x, target_y,
                   task_type, current_works, robots):

        # 机器人到达目标位置
        if plat_id == target_id:
            if task_type == 0:
                sys.stdout.write('buy %d\n' % robot_id)
            if task_type == 1:
                sys.stdout.write('sell %d\n' % robot_id)
            self.sustain[robot_id] = 0

        # 保持状态
        if self.sustain[robot_id] > 0:
            self.sustain[robot_id] -= 1
            sys.stdout.write('rotate %d %f\n' % (robot_id, self.sustain_angle_speed[robot_id]))
            sys.stdout.write('forward %d %d\n' % (robot_id, self.sustain_line_speed[robot_id]))
            return

        Data.log_print(str(robot_id) + '正在' + str(robot_x) + '，' + str(robot_y) + '正在前往' + str(target_x) + '，' + str(target_y) + '==' + str(task_type))

        # 计算前进方向和目标方向的夹角，angle>0目标方向与前进方向夹角的方向是顺时针方向
        angle = CalculateAngle(robot_direction, target_x - robot_x, target_y - robot_y)

        if abs(angle) < abs(math.pi) / 50:
            # 当angle小于PI/50，开始降低转速
            temp = 50 * abs(angle)
            angle_speed = -temp if angle < 0 else temp
        else:
            # angle>PI/50顺时针旋转   angle<-PI/50逆时针旋转
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
            line_speed = 0.5
            self.set_sustain(robot_id, line_speed, angle_speed, 30)
        elif self.is_close[robot_id] == 1:
            line_speed = - (distance/2-1) ** 2 + 6
            # line_speed = math.sqrt(distance * 2) + 4
        # elif distance < 1.5:  # 到达目的地
        #     line_speed = 4 + distance / 1.2 * 0.5
        elif angle_towards_destination > 60:  # 角度过大（0~6）
            line_speed = - (1/20) * angle_towards_destination + 9
        else:  # 对准了就冲吧
            line_speed = 6

        # 防撞边缘
        temp_angle = 5/6 * math.pi
        angle_direction = abs(angle_speed) / angle_speed if angle_speed != 0 else 1
        duration = line_speed/6*40
        a = line_speed/4
        if robot_x < a and abs(CalculateAngle(robot_direction, 1, 0)) >= temp_angle:
            self.set_sustain(robot_id, 0, angle_direction * math.pi, duration)
        # 接近右边墙并且朝向和右边墙边墙的法向量大于90°，说明会撞墙，要减速转头
        elif robot_x > 50-a and abs(CalculateAngle(robot_direction, -1, 0)) >= temp_angle:
            self.set_sustain(robot_id, 0, angle_direction * math.pi, duration)
        elif robot_y < a and abs(CalculateAngle(robot_direction, 0, 1)) >= temp_angle:
            self.set_sustain(robot_id, 0, angle_direction * math.pi, duration)
        elif robot_y > 50-a and abs(CalculateAngle(robot_direction, 0, -1)) >= temp_angle:
            self.set_sustain(robot_id, 0, angle_direction * math.pi, duration)

        # 防止同时到达相同目标点
        remain_distance = current_works.remain_distance
        for i in range(4):
            if i != robot_id and current_works.list[i] is not None:
                target_i = current_works.list[i].start if current_works.list[i].state == 0 else current_works.list[i].end
                if target_i.id == target_id \
                        and abs(remain_distance[i] - remain_distance[robot_id]) < 2 and remain_distance[robot_id] > remain_distance[i]:
                    line_speed -= 2

        # 当前机器人到robot的连线向量和当前机器人之间的夹角（负逆时针，正顺时针）
        self.get_line_toward_angle(robots)

        # 防撞
        for robot in robots:
            if robot.id == robot_id:
                continue

            # 当前机器人到robot的连线向量和当前机器人之间的夹角（负逆时针，正顺时针）
            # toward_to_line = CalculateAngle(robot_direction, robot.x - robot_x, robot.y - robot_y)

            # 预测t秒后的世界线
            t = 0.3

            # 检测t秒内是否会发生碰撞
            is_crush = False
            for i in range(math.ceil(t/0.08)):
                temp_t = i * 0.08
                x1, y1 = robot_x + robot_speed_x * temp_t, robot_y + robot_speed_y * temp_t
                x2, y2 = robot.x + robot.line_speed_x * temp_t, robot.y + robot.line_speed_y * temp_t
                if Data.calDistance(x1, y1, x2, y2) < 1.06:
                    is_crush = True
                    break

            # 发生碰撞
            critical_angle = math.pi/4
            if is_crush:
                if self.sustain[robot.id] != 0:
                    continue

                duration = 0
                toward_to_line = self.robots_toward_to_line[robot_id][robot.id]

                # 侧面直接撞
                if abs(toward_to_line) < math.pi / 20:
                    # 与大角相反方向
                    temp = -1 * abs(self.robots_toward_to_line[robot.id][robot_id]) / self.robots_toward_to_line[robot.id][robot_id]
                    angle_speed = temp * math.pi
                # 异侧撞
                elif toward_to_line * self.robots_toward_to_line[robot.id][robot_id] > 0:
                    # 反向让路
                    if abs(toward_to_line) < abs(self.robots_toward_to_line[robot.id][robot_id]):
                        if toward_to_line > 0:
                            angle_speed = clockwise_turn(angle_speed)
                        else:
                            angle_speed = counterclockwise_turn(angle_speed)
                        # duration = 8
                # 同侧撞
                else:
                    # toward_to_line 小的让路
                    if abs(toward_to_line) < abs(self.robots_toward_to_line[robot.id][robot_id]):
                        if toward_to_line > 0:
                            angle_speed = counterclockwise_turn(angle_speed)
                        else:
                            angle_speed = clockwise_turn(angle_speed)
                        # duration = 20

                # 持续时间
                duration = 2 + 6 * abs(robot_angle_speed - angle_speed)/math.pi

                # V2.0
                # 侧撞，左侧robot逆时针
                # if 2/3 * math.pi > toward_to_line >= critical_angle:
                #     angle_speed = counterclockwise_turn(angle_speed)
                # # 侧撞，右侧robot顺时针
                # elif -critical_angle > toward_to_line >= 2/3 * -math.pi:
                #     angle_speed = clockwise_turn(angle_speed)
                # # 面对面撞，右上侧robot在右侧，同时逆时针
                # elif critical_angle > toward_to_line >= 0:
                #     angle_speed = counterclockwise_turn(angle_speed)
                # # 面对面撞，右上侧robot在左侧，同时顺时针
                # elif 0 > toward_to_line >= -critical_angle:
                #     angle_speed = clockwise_turn(angle_speed)

                # V1.0
                # if abs(robot_direction - robot.towards) > math.pi/3:
                # if robot_x != robot.x and (robot_y - robot.y) / (robot_x - robot.x) < 0:
                #     # 侧撞，左侧robot逆时针
                #     if math.pi / 2 > toward_to_line >= critical_angle:
                #         angle_speed = counterclockwise_turn(angle_speed)
                #     # 侧撞，右侧robot顺时针
                #     elif -critical_angle > toward_to_line >= -math.pi / 2:
                #         angle_speed = clockwise_turn(angle_speed)
                #     # 面对面撞，右上侧robot在右侧，同时逆时针
                #     elif critical_angle > toward_to_line >= 0:
                #         angle_speed = counterclockwise_turn(angle_speed)
                #     # 面对面撞，右上侧robot在左侧，同时顺时针
                #     elif 0 > toward_to_line >= -critical_angle:
                #         angle_speed = clockwise_turn(angle_speed)
                # else:
                #     # 侧撞，左侧robot逆时针
                #     if math.pi/2 > toward_to_line >= math.pi/6:
                #         angle_speed = counterclockwise_turn(angle_speed)
                #     # 侧撞，右侧robot顺时针
                #     elif -math.pi/6 > toward_to_line >= -math.pi/2:
                #         angle_speed = clockwise_turn(angle_speed)
                #     # 面对面撞，右上侧robot在右侧，同时逆时针
                #     elif math.pi/6 > toward_to_line >= 0:
                #         angle_speed = counterclockwise_turn(angle_speed)
                #     # 面对面撞，右上侧robot在左侧，同时顺时针
                #     elif 0 > toward_to_line >= -math.pi/6:
                #         angle_speed = clockwise_turn(angle_speed)

                # line_speed = line_speed - 1 if line_speed < 1 else 1
                self.set_sustain(robot_id, line_speed, angle_speed, duration)

        Data.log_print("angle_speed" + str(robot_id) + '==' + str(angle_speed))
        Data.log_print("line_speed" + str(robot_id) + '==' + str(line_speed))
        sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))

    def set_sustain(self, robot_id, line_speed, angle_speed, frame):
        self.sustain[robot_id] = frame
        self.sustain_line_speed[robot_id] = line_speed
        self.sustain_angle_speed[robot_id] = angle_speed

    def get_line_toward_angle(self, robots):
        self.robots_toward_to_line = np.zeros((4, 4))
        for robot in robots:
            for i in range(4):
                if i == robot.id:
                    continue

                self.robots_toward_to_line[robot.id][i] = CalculateAngle(robot.towards, robots[i].x - robot.x, robots[i].y - robot.y)


# 计算 direction方向 和 (target_x,target_y)方向 的夹角，以 direction方向 为起始方向，正逆负顺
def CalculateAngle(direction, target_x, target_y):
    angle = math.atan2(target_y, target_x) - direction
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    return angle


def clockwise_turn(angle_speed):
    angle_speed -= critical_change if angle_speed < -critical_change else -math.pi
    # return angle_speed
    # return 1/3 * angle_speed + 2/3 * math.pi
    return math.pi

def counterclockwise_turn(angle_speed):
    angle_speed += critical_change if angle_speed > critical_change else math.pi
    # return angle_speed
    # return 1/3 * angle_speed - 2/3 * math.pi
    return -math.pi
