import math
import sys

import Data


def CalculateAngle(direction: object, target_x: object, target_y: object) -> object:
    angle = math.atan2(target_y, target_x) - direction
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    return angle


# 生成机器下一步行动的指令
def doInstruct(robot_id, plat_id, speed, direction, robot_x, robot_y, target_id, target_x, target_y, task_type, frame, task_end_type):
    if plat_id == target_id:
        if task_type == 0 and not (frame > 8500 and task_end_type == 7):
            sys.stdout.write('buy %d\n' % robot_id)
        if task_type == 1:
            sys.stdout.write('sell %d\n' % robot_id)

    Data.log_print(str(robot_id) + '正在前往' + str(target_x) + '，' + str(target_y) + '==' + str(task_type))

    z1 = target_x - robot_x
    z2 = target_y - robot_y
    angle = math.atan2(z2, z1) - direction
    distance = (z1 ** 2 + z2 ** 2) ** 0.5
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    angle_speed = -math.pi if angle < 0 else math.pi
    if abs(angle) < abs(math.pi) / 50:
        angle_speed = 0
    speed = 2 if (distance < 1.2) or abs(angle-math.pi/2)*100/math.pi < 2.5 else 6
    # speed = 2 if (distance < 1.2) else 6
    # 接近左边墙并且朝向和左边墙的法向量大于90°，说明会撞墙，要减速转头
    if robot_x < 1.2 and abs(CalculateAngle(direction, 1, 0)) >= math.pi / 1.895:
        speed = 1
    # 接近右边墙并且朝向和右边墙边墙的法向量大于90°，说明会撞墙，要减速转头
    if robot_x > 48.8 and abs(CalculateAngle(direction, -1, 0)) >= math.pi / 1.895:
        speed = 1
    if robot_y < 1.2 and abs(CalculateAngle(direction, 0, 1)) >= math.pi / 1.895:
        speed = 1
    if robot_y > 48.8 and abs(CalculateAngle(direction, 0, -1)) >= math.pi / 1.895:
        speed = 1
    sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
    sys.stdout.write('forward %d %d\n' % (robot_id, speed))
