import math
import sys

import numpy as np

from map1 import Data

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
                   task_type, current_works, robots, node_ids):

        # 机器人到达目标位置
        if plat_id == target_id:
            if task_type == 0 and node_ids[target_id].product_state == 1:
                sys.stdout.write('buy %d\n' % robot_id)
            elif task_type == 1 and Data.have_space(node_ids[plat_id].material_state, robots[robot_id].thing_type):
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

        Data.log_print(str(robot_id) + '正在' + str(robot_x) + '，' + str(robot_y) + '正在前往' + str(target_x) + '，' + str(
            target_y) + '==' + str(task_type))

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
        temp_angle = 1 / 6 * math.pi
        angle_direction = abs(robot_direction) / robot_direction if robot_direction != 0 else 1

        # 防止角落碰撞
        distance_1 = current_speed/6 * 1.2 + 0.5
        duration_1 = current_speed/6 * 10 + 15
        # 防止墙壁碰撞
        distance_2 = current_speed/6 * 1.2 + 0.5
        duration_2 = current_speed/6 * 10 + 10
        # 防止多球在四个角落的碰撞
        distance_3 = 6

        # 防止角落碰撞
        if robot_y < distance_1 and robot_x < distance_1 and abs(CalculateAngle(robot_direction, -1, -1)) <= temp_angle:
            angle_speed = math.pi if robot_direction > -3/4*math.pi else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration_1)
            return
        elif robot_y < distance_1 and robot_x > 50 - distance_1 and abs(CalculateAngle(robot_direction, 1, -1)) <= temp_angle:
            angle_speed = math.pi if robot_direction > -1/4*math.pi else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration_1)
            return
        elif robot_y > 50 - distance_1 and robot_x < distance_1 and abs(CalculateAngle(robot_direction, -1, 1)) <= temp_angle:
            angle_speed = math.pi if robot_direction > 3/4*math.pi else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration_1)
            return
        elif robot_y > 50 - distance_1 and robot_x > 50 - distance_1 and abs(CalculateAngle(robot_direction, 1, 1)) <= temp_angle:
            angle_speed = math.pi if robot_direction > 1/4*math.pi else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration_1)
            return
        # 防止墙壁碰撞
        elif robot_x < distance_2 and abs(CalculateAngle(robot_direction, -1, 0)) <= temp_angle:
            angle_speed = math.pi if robot_direction > 0 else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration_2)
            return
        elif robot_x > 50 - distance_2 and abs(CalculateAngle(robot_direction, 1, 0)) <= temp_angle:
            angle_speed = math.pi if robot_direction > 0 else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration_2)
            return
        elif robot_y < distance_2 and abs(CalculateAngle(robot_direction, 0, -1)) <= temp_angle:
            angle_speed = math.pi if standardization(robot_direction+1/2*math.pi) > 0 else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration_2)
            return
        elif robot_y > 50 - distance_2 and abs(CalculateAngle(robot_direction, 0, 1)) <= temp_angle:
            angle_speed = math.pi if standardization(robot_direction-1/2*math.pi) > 0 else -math.pi
            self.set_sustain(robot_id, 0, angle_speed, duration_2)
            return
        # 防止多球在四个角落的碰撞
        elif robot_y < distance_3 and robot_x < distance_3 and abs(CalculateAngle(robot_direction, -1, -1)) <= temp_angle*2 and self.will_crush(robot_id, robots, 1):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return
        elif robot_y < distance_3 and robot_x > 50 - distance_3 and abs(CalculateAngle(robot_direction, 1, -1)) <= temp_angle*2 and self.will_crush(robot_id, robots, 2):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return
        elif robot_y > 50 - distance_3 and robot_x < distance_3 and abs(CalculateAngle(robot_direction, -1, 1)) <= temp_angle*2 and self.will_crush(robot_id, robots, 3):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return
        elif robot_y > 50 - distance_3 and robot_x > 50 - distance_3 and abs(CalculateAngle(robot_direction, 1, 1)) <= temp_angle*2 and self.will_crush(robot_id, robots, 4):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return
        elif robot_y > 46 and abs(CalculateAngle(robot_direction, 0, 1)) <= temp_angle and self.will_crush(robot_id, robots, 5):
            self.set_sustain(robot_id, 0, angle_speed, 5)
            return


        # 防止同时到达相同目标点
        parameter_1 = current_speed/6 * 1.2 + 1.2  # 前后保持的距离
        # parameter_1 = 4 if node_ids[target_id].type in [1] else current_speed / 6 * 1.2 + 1.8 # 前后保持的距离
        remain_distance = current_works.remain_distance
        for i in range(4):
            if i != robot_id and current_works.list[i] is not None:
                target_i = current_works.list[i].start if current_works.list[i].state == 0 else current_works.list[i].end
                if target_i.id == target_id \
                        and abs(remain_distance[i] - remain_distance[robot_id]) < parameter_1 and remain_distance[robot_id] > remain_distance[i]:
                    line_speed = 0

        # 当前机器人到robot的连线向量和当前机器人之间的夹角（正逆负顺）每一帧更新一次
        if robot_id == 0:
            self.get_line_toward_angle(robots)

        # 防撞
        for robot in robots:
            if robot.id == robot_id:
                continue

            # 预测t秒后的世界线
            t = 0.3

            # 检测t秒内是否会发生碰撞
            is_crush = False
            for i in range(math.ceil(t / 0.08)):
                temp_t = i * 0.08
                x1, y1 = robot_x + robot_speed_x * temp_t, robot_y + robot_speed_y * temp_t
                x2, y2 = robot.x + robot.line_speed_x * temp_t, robot.y + robot.line_speed_y * temp_t
                if Data.calDistance_precise(x1, y1, x2, y2) < 1.06:
                    # and abs(robot_angle_speed) < math.pi / 2 and abs(robot.angle_speed) < math.pi / 2 \
                    is_crush = True
                    break

            # 发生碰撞
            critical_angle = math.pi / 4
            if is_crush:

                duration_2 = -1
                toward_to_line = self.robots_toward_to_line[robot_id][robot.id]
                another_toward_to_line = self.robots_toward_to_line[robot.id][robot_id]

                # 大角撞
                if abs(robot_direction - robot.towards) >= critical_angle:
                    # if abs(toward_to_line) < math.pi/18 or abs(another_toward_to_line) < math.pi/18:
                    # 异侧撞，面对面
                    if toward_to_line * another_toward_to_line > 0:
                        if toward_to_line > 0:
                            angle_speed = clockwise_turn(angle_speed)
                        else:
                            angle_speed = counterclockwise_turn(angle_speed)
                        duration_2 = 8
                    # 侧面偷袭
                    elif abs(toward_to_line) < math.pi / 7 and abs(toward_to_line) < abs(another_toward_to_line):
                        temp = -1 * abs(another_toward_to_line) / another_toward_to_line
                        angle_speed = temp * math.pi
                        line_speed -= 1 if line_speed > 1 else 0
                        duration_2 = 8
                    elif abs(another_toward_to_line) < math.pi / 7 and abs(another_toward_to_line) < abs(toward_to_line):
                        temp = -1 * abs(toward_to_line) / toward_to_line
                        angle_speed = temp * abs(another_toward_to_line)
                        duration_2 = (math.pi - abs(another_toward_to_line))/math.pi*5
                    # 同侧撞
                    else:
                        k = (robot.y - robot_y) / (robot.x - robot_x)
                        if k > 0:
                            angle_speed = counterclockwise_turn(angle_speed)
                        else:
                            angle_speed = clockwise_turn(angle_speed)
                        duration_2 = 8 + (math.pi - abs(robot_direction - robot.towards)) / (3 / 2 * math.pi) * 15
                # 小角撞
                else:
                    robot_speed = (robot.line_speed_x ** 2 + robot.line_speed_y ** 2) ** 0.5
                    # 追尾
                    if abs(current_speed - robot_speed) > 2 and current_speed > robot_speed:
                        sign = -1 * toward_to_line / abs(toward_to_line)
                        angle_speed = sign * math.pi
                        duration_2 = 10
                    # 侧撞
                    else:
                        if abs(toward_to_line) < abs(self.robots_toward_to_line[robot.id][robot_id]):
                            line_speed = 0
                            duration_2 = 15

                if duration_2 > 0:
                    if line_speed < 4:
                        line_speed = 4
                    if robot.thing_type == 7:
                        line_speed = 2
                    if robot_angle_speed * angle_speed < -math.pi:
                        line_speed = 2
                    if robot.thing_type != 0 or robots[robot_id].thing_type != 0:
                        duration_2 = 3
                    # 边缘碰撞
                    # distance_3 = 3
                    # par_4 = 1/2*math.pi
                    # if (robot.x < distance_3 or robot.y < distance_3 or robot.x > 50-distance_3 or robot.y > 50-distance_3) \
                    #         and (abs(CalculateAngle(robot_direction, -1, 1))>par_4 or abs(CalculateAngle(robot_direction, -1, 1))>par_4 or
                    #          abs(CalculateAngle(robot_direction, -1, 1))>par_4 or abs(CalculateAngle(robot_direction, -1, 1))>par_4):
                    #     angle_speed *= 1/2
                    #     line_speed = 0
                        # duration_2 *= 2

                    self.set_sustain(robot_id, line_speed, angle_speed, duration_2)
                    Data.log_print("检测到碰撞" + str(robot_id) + ',' + str(robot.id) + ',' + str(line_speed) + ',' + str(
                        angle_speed) + ',' + str(duration_2))

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

                self.robots_toward_to_line[robot.id][i] = CalculateAngle(robot.towards, robots[i].x - robot.x,
                                                                         robots[i].y - robot.y)

    def will_crush(self, robot_id, robots, type):
        for robot in robots:
            if robot.id == robot_id:
                continue
            if type==1 and robot.x < robots[robot_id].x and robot.y < robots[robot_id].y:
                return True
            elif type==2 and robot.x > robots[robot_id].x and robot.y < robots[robot_id].y:
                return True
            elif type==3 and robot.x < robots[robot_id].x and robot.y > robots[robot_id].y:
                return True
            elif type==4 and robot.x > robots[robot_id].x and robot.y > robots[robot_id].y:
                return True
            elif type==5 and robot.y > robots[robot_id].y:
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


def standardization(angle):
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    return angle