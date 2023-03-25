import math
import sys

import numpy as np

critical_change = 2 * math.pi


class Physics:

    def __init__(self):
        self.is_close = [-1, -1, -1, -1]  # 1为已接近；-1为未接近
        self.target = [-1, -1, -1, -1]  # -1为初始化

        self.sustain = [0, 0, 0, 0]
        self.sustain_line_speed = [0, 0, 0, 0]
        self.sustain_angle_speed = [0, 0, 0, 0]

        self.robots_toward_to_line = []

        self.being_spin = [-1, -1, -1, -1]

    # 生成机器下一步行动的指令
    def doInstruct(self, robot_id, plat_id, robot_direction, robot_x, robot_y, robot_angle_speed, robot_speed_x,
                   robot_speed_y, target_id, target_x, target_y,
                   task_type, robot_infos, worker_num):

        # 机器人到达目标位置
        if plat_id == target_id:
            if plat_id == target_id:  # 机器人所处位置 == 目标位置
                if task_type == 0:
                    sys.stdout.write('buy %d\n' % robot_id)
                if task_type == 1:
                    sys.stdout.write('sell %d\n' % robot_id)
                self.sustain[robot_id] = 0
            else:
                sys.stdout.write('rotate %d %f\n' % (robot_id, 0))
                sys.stdout.write('forward %d %d\n' % (robot_id, 0))

        # 保持状态
        if self.sustain[robot_id] > 0:
            self.sustain[robot_id] -= 1
            sys.stdout.write('rotate %d %f\n' % (robot_id, self.sustain_angle_speed[robot_id]))
            sys.stdout.write('forward %d %d\n' % (robot_id, self.sustain_line_speed[robot_id]))
            return


        # 从机器人运动方向出发，与目标点方向，之间的夹角大小，angle>0运动方向出发到目标方向的夹角的方向是顺时针方向
        angle = CalculateAngle(robot_direction, target_x - robot_x, target_y - robot_y)
        # 当前速度大小
        current_speed = (robot_speed_x ** 2 + robot_speed_y ** 2) ** 0.5
        # 距离目标点路径长度
        distance = ((target_x - robot_x) ** 2 + (target_y - robot_y) ** 2) ** 0.5

        # 角速度定义
        if abs(angle) < abs(math.pi) / 50:
            # 当angle小于PI/50，开始降低转速
            temp = 50 * abs(angle)
            angle_speed = -temp if angle < 0 else temp
        else:
            # angle>PI/50顺时针旋转   angle<-PI/50逆时针旋转
            angle_speed = -math.pi if angle < 0 else math.pi

        # 更新state、target。目的：防止绕圈
        old_target_robot = self.target[robot_id]
        self.target[robot_id] = target_id
        if distance < 2:
            self.is_close[robot_id] = 1
        if self.is_close[robot_id] == 1 and old_target_robot != self.target[robot_id]:
            self.is_close[robot_id] = -1
        # 速度定义
        angle_towards_destination = abs(angle) * 180 / math.pi

        if angle_towards_destination < 40 and self.being_spin[robot_id] == 1:
            self.being_spin[robot_id] = -1
        if self.is_close[robot_id] == 1 and (angle_towards_destination > 80 or self.being_spin[robot_id] == 1):  # 开始绕圈
            line_speed = 1
            self.being_spin[robot_id] = 1
        elif self.is_close[robot_id] == 1:  # 接近目的地
            line_speed = - (distance / 2 - 1) ** 2 + 6
            # line_speed = math.sqrt(distance * 2) + 4
        elif angle_towards_destination > 60:  # 角度过大（0~6）
            line_speed = - (1 / 20) * angle_towards_destination + 9
        else:  # 对准了就冲吧
            line_speed = 6

        # 防撞墙
        # if robots[robot_id].thing_type != 0:
        temp_angle = 1 / 6 * math.pi
        angle_direction = abs(robot_direction) / robot_direction if robot_direction != 0 else 1
        duration = current_speed / 6 * 30
        a = current_speed / 6 * 2
        par_1 = 0.9
        par_2 = 0.9 if worker_num == 43 else 1
        par_3 = 4
        if robot_x < a and abs(CalculateAngle(robot_direction, -1, 0)) <= temp_angle:
            self.set_sustain(robot_id, 0, angle_direction * math.pi, duration)
            return
        elif robot_x > 50 - a and abs(CalculateAngle(robot_direction, 1, 0)) <= temp_angle:
            self.set_sustain(robot_id, 0, angle_direction * math.pi, duration)
            return
        elif robot_y < a and abs(CalculateAngle(robot_direction, 0, -1)) <= temp_angle:
            self.set_sustain(robot_id, 0, angle_direction * math.pi, duration)
            return
        elif robot_y > 50 - a and abs(CalculateAngle(robot_direction, 0, 1)) <= temp_angle:
            self.set_sustain(robot_id, 0, angle_direction * math.pi, duration)
            return
        elif robot_y < a * par_1 and robot_x < a * par_1 and abs(
                CalculateAngle(robot_direction, -1, -1)) <= temp_angle * 2:
            angle_speed = math.pi if robot_direction > -3 / 4 * math.pi or robot_angle_speed > 0 else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration * par_2)
            return
        elif robot_y < a * par_1 and robot_x > 50 - a * par_1 and abs(
                CalculateAngle(robot_direction, 1, -1)) <= temp_angle * 2:
            angle_speed = math.pi if robot_direction > -1 / 4 * math.pi or robot_angle_speed > 0 else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration * par_2)
            return
        elif robot_y > 50 - a * par_1 and robot_x < a * par_1 and abs(
                CalculateAngle(robot_direction, -1, 1)) <= temp_angle * 2:
            angle_speed = math.pi if robot_direction > 3 / 4 * math.pi or robot_angle_speed > 0 else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration * par_2)
            return
        elif robot_y > 50 - a * par_1 and robot_x > 50 - a * par_1 and abs(
                CalculateAngle(robot_direction, 1, 1)) <= temp_angle * 2:
            angle_speed = math.pi if robot_direction > 1 / 4 * math.pi or robot_angle_speed > 0 else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration * par_2)
            return
        # 防止边缘碰撞
        elif robot_y < par_3 and robot_x < par_3 and abs(
                CalculateAngle(robot_direction, -1, -1)) <= temp_angle * 2 and self.will_crush(robot_id, robot_infos, 1):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return
        elif robot_y < par_3 and robot_x > 50 - par_3 and abs(
                CalculateAngle(robot_direction, 1, -1)) <= temp_angle * 2 and self.will_crush(robot_id, robot_infos, 2):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return
        elif robot_y > 50 - par_3 and robot_x < par_3 and abs(
                CalculateAngle(robot_direction, -1, 1)) <= temp_angle * 2 and self.will_crush(robot_id, robot_infos, 3):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return
        elif robot_y > 50 - par_3 and robot_x > 50 - par_3 and abs(
                CalculateAngle(robot_direction, 1, 1)) <= temp_angle * 2 and self.will_crush(robot_id, robot_infos, 4):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return
        # 左下
        # elif robot_y < a*par_1 and robot_x < a*par_1 and abs(CalculateAngle(robot_direction, -1, -1)) <= temp_angle*2:
        #     angle_speed = math.pi if robot_direction > -3/4*math.pi else -math.pi
        #     angle_speed = abs(robot_angle_speed)/robot_angle_speed*math.pi if abs(robot_angle_speed) > 1/3*math.pi else angle_speed
        #     self.set_sustain(robot_id, 0, angle_speed, duration*par_2)
        #     return
        # # 右下
        # elif robot_y < a*par_1 and robot_x > 50 - a*par_1 and abs(CalculateAngle(robot_direction, 1, -1)) <= temp_angle*2:
        #     angle_speed = math.pi if robot_direction > -1/4*math.pi else -math.pi
        #     angle_speed = abs(robot_angle_speed)/robot_angle_speed*math.pi if abs(robot_angle_speed) > 1/3*math.pi else angle_speed
        #     self.set_sustain(robot_id, 0, angle_speed, duration*par_2)
        #     return
        # # 左上
        # elif robot_y > 50 - a*par_1 and robot_x < a*par_1 and abs(CalculateAngle(robot_direction, -1, 1)) <= temp_angle*2:
        #     angle_speed = math.pi if robot_direction > 3/4*math.pi else -math.pi
        #     angle_speed = abs(robot_angle_speed)/robot_angle_speed*math.pi if abs(robot_angle_speed) > 1/3*math.pi else angle_speed
        #     self.set_sustain(robot_id, 0, angle_speed, duration*par_2)
        #     return
        # # 右上
        # elif robot_y > 50 - a*par_1 and robot_x > 50 - a*par_1 and abs(CalculateAngle(robot_direction, 1, 1)) <= temp_angle*2:
        #     angle_speed = math.pi if robot_direction > 1/4*math.pi else -math.pi
        #     angle_speed = abs(robot_angle_speed)/robot_angle_speed*math.pi if abs(robot_angle_speed) > 1/3*math.pi else angle_speed
        #     self.set_sustain(robot_id, 0, angle_speed, duration*par_2)
        #     return

        # 防止同时到达相同目标点
        parameter_1 = current_speed / 6 + 2  # 前后保持的距离
        # parameter_1 = current_speed / 6 * 1.2 + 2 if node_ids[target_id].type in [1, 2,
        #                                                                           3] else current_speed / 6 * 1.2 + 1.1  # 前后保持的距离
        # remain_distance = current_works.remain_distance
        # for i in range(4):
        #     if i != robot_id and current_works.list[i] is not None:
        #         target_i = current_works.list[i].start if current_works.list[i].state == 0 else current_works.list[
        #             i].end
        #         if target_i.id == target_id \
        #                 and abs(remain_distance[i] - remain_distance[robot_id]) < parameter_1 and remain_distance[
        #             robot_id] > remain_distance[i]:
        #             line_speed = 0

        # 当前机器人到robot的连线向量和当前机器人之间的夹角（正逆负顺）每一帧更新一次
        if robot_id == 0:
            self.get_line_toward_angle(robot_infos)

        # 防撞
        for i in range(4):
            if robot_id == i:
                continue

            # 预测t秒后的世界线
            t = 0.3

            # 检测t秒内是否会发生碰撞
            is_crush = False
            for j in range(math.ceil(t / 0.08)):
                temp_t = j * 0.08
                x1, y1 = robot_x + robot_speed_x * temp_t, robot_y + robot_speed_y * temp_t
                x2, y2 = robot_infos[i][7] + robot_infos[i][9] * temp_t, robot_infos[i][8] + robot_infos[i][10] * temp_t
                if ((x1-x2)**2+(y1-y2)**2)**0.5 < 1.06:
                    # and abs(robot_angle_speed) < math.pi / 2 and abs(robot.angle_speed) < math.pi / 2 \
                    is_crush = True
                    break

            # 发生碰撞
            critical_angle = math.pi / 4
            if is_crush:
                # if self.sustain[robot.id] != 0:
                #     continue

                duration = -1
                toward_to_line = self.robots_toward_to_line[robot_id][i]
                another_toward_to_line = self.robots_toward_to_line[i][robot_id]

                # 大角撞
                if abs(robot_direction - robot_infos[i][6]) >= critical_angle:
                    # if abs(toward_to_line) < math.pi/18 or abs(another_toward_to_line) < math.pi/18:
                    # 异侧撞，面对面
                    if toward_to_line * another_toward_to_line > 0:
                        if toward_to_line > 0:
                            angle_speed = clockwise_turn(angle_speed)
                        else:
                            angle_speed = counterclockwise_turn(angle_speed)
                        duration = 8
                    # 侧面偷袭
                    elif abs(toward_to_line) < math.pi / 7 and abs(toward_to_line) < abs(another_toward_to_line):
                        temp = -1 * abs(another_toward_to_line) / another_toward_to_line
                        angle_speed = temp * math.pi
                        line_speed -= 1 if line_speed > 1 else 0
                        duration = 8
                    elif abs(another_toward_to_line) < math.pi / 7 and abs(another_toward_to_line) < abs(
                            toward_to_line):
                        temp = -1 * abs(toward_to_line) / toward_to_line
                        angle_speed = temp * abs(another_toward_to_line)
                        duration = (math.pi - abs(another_toward_to_line)) / math.pi * 5
                    # elif abs(toward_to_line) < math.pi / 7 and math.pi / 2.2 < abs(another_toward_to_line):
                    #     temp = -1 * abs(another_toward_to_line) / another_toward_to_line
                    #     angle_speed = temp * math.pi
                    #     line_speed -= 1 if line_speed > 1 else 0
                    #     duration = 8
                    # elif abs(another_toward_to_line) < math.pi / 7 and math.pi / 2.2 < abs(toward_to_line):
                    #     temp = -1 * abs(another_toward_to_line) / another_toward_to_line
                    #     angle_speed = temp * 1/3 * math.pi
                    #     line_speed += 4 if line_speed < 4 else 6
                    #     duration = 5
                    # 同侧撞
                    else:
                        k = (robot_infos[i][8] - robot_y) / (robot_infos[i][7] - robot_x)
                        if k > 0:
                            angle_speed = counterclockwise_turn(angle_speed)
                        else:
                            angle_speed = clockwise_turn(angle_speed)
                        duration = 8 + (math.pi - abs(robot_direction - robot_infos[i][6])) / (3 / 2 * math.pi) * 15
                # 小角撞
                else:
                    robot_speed = (robot_infos[i][9] ** 2 + robot_infos[i][10] ** 2) ** 0.5
                    # 追尾
                    if abs(current_speed - robot_speed) > 2 and current_speed > robot_speed:
                        sign = -1 * toward_to_line / abs(toward_to_line)
                        angle_speed = sign * math.pi
                        duration = 10
                    # 侧撞
                    else:
                        if abs(toward_to_line) < abs(self.robots_toward_to_line[i][robot_id]):
                            line_speed = 0
                            duration = 15

                if duration > 0:
                    if line_speed < 4:
                        line_speed = 4
                    if robot_infos[i][1] == 7:
                        line_speed = 2
                    if robot_angle_speed * angle_speed < -math.pi:
                        line_speed = 2
                    if robot_infos[i][1] != 0 or robot_infos[robot_id][1] != 0:
                        duration = 3
                    # 边缘碰撞
                    # par_3 = 3
                    # par_4 = 1/2*math.pi
                    # if (robot.x < par_3 or robot.y < par_3 or robot.x > 50-par_3 or robot.y > 50-par_3) \
                    #         and (abs(CalculateAngle(robot_direction, -1, 1))>par_4 or abs(CalculateAngle(robot_direction, -1, 1))>par_4 or
                    #          abs(CalculateAngle(robot_direction, -1, 1))>par_4 or abs(CalculateAngle(robot_direction, -1, 1))>par_4):
                    #     angle_speed *= 1/2
                    #     line_speed = 0
                    # duration *= 2

                    self.set_sustain(robot_id, line_speed, angle_speed, duration)
                # V3.0
                # 侧面直接撞
                # if abs(toward_to_line) < math.pi / 20:
                #     # 与大角相反方向
                #     temp = -1 * abs(self.robots_toward_to_line[robot.id][robot_id]) / self.robots_toward_to_line[robot.id][robot_id]
                #     angle_speed = temp * math.pi
                #     duration = 8
                # # 异侧撞
                # elif toward_to_line * self.robots_toward_to_line[robot.id][robot_id] > 0:
                #     # 反向让路
                #     if abs(toward_to_line) < abs(self.robots_toward_to_line[robot.id][robot_id]):
                #         if toward_to_line > 0:
                #             angle_speed = clockwise_turn(angle_speed)
                #         else:
                #             angle_speed = counterclockwise_turn(angle_speed)
                #     duration = 8
                # # 同侧撞
                # else:
                #     # toward_to_line 小的让路
                #     if abs(toward_to_line) < abs(self.robots_toward_to_line[robot.id][robot_id]):
                #         if toward_to_line > 0:
                #             angle_speed = counterclockwise_turn(angle_speed)
                #         else:
                #             angle_speed = clockwise_turn(angle_speed)
                #     duration = 20

                # 持续时间
                # duration = 2 + 6 * abs(robot_angle_speed - angle_speed)/math.pi

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

        sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
        sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))

    def set_sustain(self, robot_id, line_speed, angle_speed, frame):
        self.sustain[robot_id] = frame
        self.sustain_line_speed[robot_id] = line_speed
        self.sustain_angle_speed[robot_id] = angle_speed

    def get_line_toward_angle(self, robot_infos):
        self.robots_toward_to_line = np.zeros((4, 4))
        for i in range(4):
            for j in range(4):
                if i == j:
                    continue
                self.robots_toward_to_line[i][j] = CalculateAngle(robot_infos[i][6], robot_infos[j][7] - robot_infos[i][7],
                                                                         robot_infos[j][8] - robot_infos[i][8])

    def will_crush(self, robot_id, robot_infos, type):
        for robot in range(4):
            if robot_id == robot:
                continue
            if type == 1 and robot_infos[robot][7] < robot_infos[robot_id][7] and robot_infos[robot][8] < robot_infos[robot_id][8]:
                return True
            elif type == 2 and robot_infos[robot][7] > robot_infos[robot_id][7] and robot_infos[robot][8] < robot_infos[robot_id][8]:
                return True
            elif type == 3 and robot_infos[robot][7] < robot_infos[robot_id][7] and robot_infos[robot][8] > robot_infos[robot_id][8]:
                return True
            elif type == 4 and robot_infos[robot][7] > robot_infos[robot_id][7] and robot_infos[robot][8] > robot_infos[robot_id][8]:
                return True
        return False


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
    return -math.pi


def counterclockwise_turn(angle_speed):
    angle_speed += critical_change if angle_speed > critical_change else math.pi
    # return angle_speed
    # return 1/3 * angle_speed - 2/3 * math.pi
    return math.pi




# import math
# import sys
#
# class Physics:
#     def __init__(self):
#         self.is_close = [-1, -1, -1, -1]  # 1为已接近；-1为未接近
#         self.target = [-1, -1, -1, -1]  # -1为初始化
#     # 生成机器下一步行动的指令
#     def doInstruct(self, robot_id, plat_id,  direction, robot_x, robot_y, target_id, target_x, target_y,
#                    task_type):
#         if plat_id == target_id:  # 机器人所处位置 == 目标位置
#             if task_type == 0:
#                 sys.stdout.write('buy %d\n' % robot_id)
#             if task_type == 1:
#                 sys.stdout.write('sell %d\n' % robot_id)
#         # 计算前进方向和目标方向的夹角，angle>0目标方向与前进方向夹角的方向是顺时针方向
#         angle = CalculateAngle(direction, target_x - robot_x, target_y - robot_y)
#
#         if abs(angle) < abs(math.pi) / 50:
#             # 当angle小于PI/50，开始降低转速
#             angle_speed = 0
#         else:
#             # angle>PI/50顺时针旋转，angle<-PI/50逆时针旋转
#             angle_speed = -math.pi if angle < 0 else math.pi
#         distance = ((target_x - robot_x) ** 2 + (target_y - robot_y) ** 2) ** 0.5
#         # 更新state、target
#         old_target_robot = self.target[robot_id]
#         self.target[robot_id] = target_id
#         if distance < 2:
#             self.is_close[robot_id] = 1
#         if self.is_close[robot_id] == 1 and old_target_robot != self.target[robot_id]:
#             self.is_close[robot_id] = -1
#         # 速度定义
#         angle_towards_destination = abs(angle) * 180 / math.pi
#         if self.is_close[robot_id] == 1 and angle_towards_destination > 80:  # 开始绕圈
#             line_speed = 0.5
#         elif distance < 1.2:  # 到达目的地
#             line_speed = 1.5 + distance / 1.2 * 0.5
#         elif angle_towards_destination > 60:  # 角度过大（0~6）
#             line_speed = - (1/20) * angle_towards_destination + 9
#         else:  # 对准了就冲吧
#             line_speed = 6
#             # 防撞墙分级减速！
#         wall_speed_list = [6, 4, 2, 0]
#         level = 0
#         limit_speed=6
#         if robot_x < 2:
#             level = wallSpeedControl(direction, -1, 0)
#         if robot_x > 48:
#             level = wallSpeedControl(direction, 1, 0)
#         if robot_y < 2:
#             level = wallSpeedControl(direction, 0, -1)
#         if robot_y > 48:
#             level = wallSpeedControl(direction, 0, 1)
#         if isCloseCorner(direction, robot_x, robot_y) == 1:
#             limit_speed = 1
#         sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
#         sys.stdout.write('forward %d %d\n' % (robot_id, min(limit_speed, line_speed, 6, wall_speed_list[level])))
#
# def CalculateAngle(direction, target_x, target_y):
#     angle = math.atan2(target_y, target_x) - direction
#     if angle > math.pi:
#         angle -= 2 * math.pi
#     if angle < -math.pi:
#         angle += 2 * math.pi
#     return angle
#
# def wallSpeedControl(direction, x, y):
#     level = 0
#     if abs(CalculateAngle(direction, x, y)) < math.pi / 3:
#         level = +1
#     if abs(CalculateAngle(direction, x, y)) < math.pi / 4:
#         level = +1
#     if abs(CalculateAngle(direction, x, y)) < math.pi / 6:
#         level = +1
#     return level
#
# def isCloseCorner(direction, x, y):
#     flag = 0
#     if abs(CalculateAngle(direction, 0, -1)) < math.pi / 2 or abs(CalculateAngle(direction, -1, 0)) < math.pi / 2:
#         if x < 2 and y < 2:
#             flag = 1
#     if abs(CalculateAngle(direction, 0, -1)) < math.pi / 2 or abs(CalculateAngle(direction, 1, 0)) < math.pi / 2:
#         if x > 48 and y < 2:
#             flag = 1
#     if abs(CalculateAngle(direction, 0, 1)) < math.pi / 2 or abs(CalculateAngle(direction, -1, 0)) < math.pi / 2:
#         if x < 2 and y > 48:
#             flag = 1
#     if abs(CalculateAngle(direction, 0, 1)) < math.pi / 2 or abs(CalculateAngle(direction, 1, 0)) < math.pi / 2:
#         if x > 48 and y > 48:
#             flag = 1
#     return flag