import math
import sys

import CheckCrush
import Data
import Physics

if __name__ == '__main__':

    # 初始化
    _data = Data.Data()
    _data.load()
    physics = Physics.Physics()

    get_6 = False
    start = 0
    end = 0
    while True:
        # 接收、处理数据、调度
        _data.update()

        # 发出指令
        Data.log_print('======= %d =======' % _data.frame)
        sys.stdout.write('%d\n' % _data.frame)
        for i in range(4):
            if _data.current_works.list[i] is not None:
                task = _data.current_works.list[i]
                if task.state == 0:
                    physics.doInstruct(i, _data.robot[i].node_id, _data.robot[i].towards, _data.robot[i].x, _data.robot[i].y, _data.robot[i].angle_speed, _data.robot[i].line_speed_x, _data.robot[i].line_speed_y,
                                       task.start.id, task.start.x, task.start.y, task.state,
                                       _data.current_works, _data.robot)
                else:
                    physics.doInstruct(i, _data.robot[i].node_id, _data.robot[i].towards, _data.robot[i].x, _data.robot[i].y, _data.robot[i].angle_speed, _data.robot[i].line_speed_x, _data.robot[i].line_speed_y,
                                       task.end.id, task.end.x, task.end.y, task.state,
                                       _data.current_works, _data.robot)
            else:
                physics.doInstruct(i, -1, _data.robot[i].towards, _data.robot[i].x, _data.robot[i].y, _data.robot[i].angle_speed, _data.robot[i].line_speed_x, _data.robot[i].line_speed_y,
                                   -1, _data.robot[i].x, _data.robot[i].y, -1,
                                   _data.current_works, _data.robot)


        # angle_speed = _data.robot[0].angle_speed
        # if angle_speed >= math.pi-0.001 and not get_6:
        #     get_6 = True
        #     start = _data.frame
        #     Data.log_print("=======frame=========="+str(start))
        #     Data.log_print("=======speed=========="+str(angle_speed))
        # elif angle_speed <= -math.pi+0.001 and get_6:
        #     end = _data.frame
        #     get_6 = False
        #     Data.log_print("=======frame=========="+str(end))
        #     Data.log_print("=======speed=========="+str(angle_speed))
        #
        # if not get_6:
        #     sys.stdout.write('rotate %d %f\n' % (0, math.pi))
        # else:
        #     sys.stdout.write('rotate %d %f\n' % (0, -math.pi))
        #
        # if end != 0:
        #     Data.log_print("=======frame=========="+str(end-start))

        # 结束
        Data.finish()
