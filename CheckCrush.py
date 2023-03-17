import math
import sys


def CheckCrush(robot1_id, robot1_direction, robot1_x, robot1_y, robot2_id, robot2_direction, robot2_x, robot2_y):
    if robot1_id == robot2_id:
        return
    # 计算两机器人的直线距离的平方
    distance = ((robot1_x - robot2_x) ** 2 + (robot1_y - robot2_y) ** 2) ** 0.5
    if distance < 2:  # 如果两机器人的距离小于3,碰撞发现前提
        # 计算两个机器人的朝向
        angle = (robot1_direction - robot2_direction)
        if angle > math.pi:
            angle -= 2 * math.pi
        if angle < -math.pi:
            angle += 2 * math.pi
            # 如果两个机器人的朝向夹角大于150°，当作碰撞,让他们都按一个顺序转角
        if abs(angle * 180 / math.pi) > 135:
            sys.stdout.write('rotate %d %f\n' % (robot1_id, math.pi / 3))
            sys.stdout.write('forward %d %d\n' % (robot1_id, 5))
