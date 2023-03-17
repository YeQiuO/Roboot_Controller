import math
import sys


def CheckCrush(robot1_id, robot1_direction, robot1_x, robot1_y, robot1_Vx, robot1_Vy, robot2_id, robot2_direction,
               robot2_x, robot2_y, robot2_Vx, robot2_Vy):
    if robot1_id == robot2_id:
        return
    line_angle = math.atan2(robot2_y - robot1_y, robot2_x - robot1_x)  # 以机器人1号坐标为起点到机器人二号坐标的向量，以弧度表示
    angle = line_angle - robot1_direction  # 连线向量和1号机器人之间的夹角
    if angle > math.pi:
        angle -= 2 * math.pi
    if angle < -math.pi:
        angle += 2 * math.pi
    # angle_speed = -math.pi if angle < 0 else math.pi
    distance = ((robot2_y - robot1_y) ** 2 + (robot2_x - robot1_x) ** 2) ** 0.5
    # 预测机制_预测t秒后的世界线
    t = 0.3
    # t秒后的机器人1的位置
    (x1, y1) = (robot1_x + robot1_Vx * t, robot1_y + robot1_Vy * t)
    # t秒后的机器人2的位置
    (x2, y2) = (robot2_x + robot2_Vx * t, robot2_y + robot2_Vy * t)
    if ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5 < 1.06:  # ＞1说明没有碰到了
        # sys.stderr.write("-%d号机器人：坐标：（%d, %d）和%d号机器人：坐标：（%d, %d）--碰撞！\n" % (
        #   robot1_id, robot1_x, robot1_y, robot2_id, robot2_x, robot2_y))
        if abs(robot1_direction - robot2_direction) > math.pi / 3:
            if robot1_x != robot2_x:
                k = (robot1_y - robot2_y) / (robot1_x - robot2_x)
                if k > 0:
                    sys.stdout.write('rotate %d %f\n' % (robot1_id, math.pi))
                    sys.stdout.write('rotate %d %f\n' % (robot2_id, math.pi))
                    sys.stdout.write('forward %d %d\n' % (robot1_id, 3))
                    sys.stdout.write('forward %d %d\n' % (robot2_id, 3))
                else:
                    sys.stdout.write('rotate %d %f\n' % (robot1_id, -math.pi))
                    sys.stdout.write('rotate %d %f\n' % (robot2_id, -math.pi))
                    sys.stdout.write('forward %d %d\n' % (robot1_id, 3))
                    sys.stdout.write('forward %d %d\n' % (robot2_id, 3))
            else:
                sys.stdout.write('rotate %d %f\n' % (robot1_id, math.pi))
                sys.stdout.write('rotate %d %f\n' % (robot2_id, math.pi))
                sys.stdout.write('forward %d %d\n' % (robot1_id, 3))
                sys.stdout.write('forward %d %d\n' % (robot2_id, 3))
        else:
            # return
            if robot1_x != robot2_x:
                k = (robot1_y - robot2_y) / (robot1_x - robot2_x)
                if k > 0:
                    sys.stdout.write('rotate %d %f\n' % (robot1_id, math.pi))
                    sys.stdout.write('rotate %d %f\n' % (robot2_id, -math.pi))
                    sys.stdout.write('forward %d %d\n' % (robot1_id, 1))
                    sys.stdout.write('forward %d %d\n' % (robot2_id, 1))
                else:
                    sys.stdout.write('rotate %d %f\n' % (robot1_id, -math.pi))
                    sys.stdout.write('rotate %d %f\n' % (robot2_id, math.pi))
                    sys.stdout.write('forward %d %d\n' % (robot1_id, 1))
                    sys.stdout.write('forward %d %d\n' % (robot2_id, 1))
            else:
                sys.stdout.write('rotate %d %f\n' % (robot1_id, math.pi))
                sys.stdout.write('rotate %d %f\n' % (robot2_id, math.pi))
                sys.stdout.write('forward %d %d\n' % (robot1_id, 1))
                sys.stdout.write('forward %d %d\n' % (robot2_id, 1))