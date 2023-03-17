import math
import sys

import CheckCrush
import Data
import Physics

if __name__ == '__main__':

    # 初始化
    _data = Data.Data()
    _data.load()

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
                    Physics.doInstruct(i, _data.robot[i].node_id, -1, _data.robot[i].towards, _data.robot[i].x,
                                       _data.robot[i].y,
                                       task.start.id, task.start.x, task.start.y, task.state, _data.frame, task.end.type)

                    for j in range(4):
                        CheckCrush.CheckCrush(i, _data.robot[i].towards, _data.robot[i].x,
                                              _data.robot[i].y, _data.robot[i].line_speed_x,
                                              _data.robot[i].line_speed_y, j, _data.robot[j].towards, _data.robot[j].x,
                                              _data.robot[j].y, _data.robot[j].line_speed_x,
                                              _data.robot[j].line_speed_y)
                else:
                    Physics.doInstruct(i, _data.robot[i].node_id, -1, _data.robot[i].towards, _data.robot[i].x,
                                       _data.robot[i].y,
                                       task.end.id, task.end.x, task.end.y, task.state, _data.frame, task.end.type)

                    for j in range(4):
                        CheckCrush.CheckCrush(i, _data.robot[i].towards, _data.robot[i].x,
                                              _data.robot[i].y, _data.robot[i].line_speed_x,
                                              _data.robot[i].line_speed_y, j, _data.robot[j].towards, _data.robot[j].x,
                                              _data.robot[j].y, _data.robot[j].line_speed_x,
                                              _data.robot[j].line_speed_y)
            else:
                Physics.doInstruct(i, -1, -1, _data.robot[i].towards, _data.robot[i].x, _data.robot[i].y,
                                   -1, _data.robot[i].x, _data.robot[i].y, -1, _data.frame, -1)

                for j in range(4):
                    CheckCrush.CheckCrush(i, _data.robot[i].towards, _data.robot[i].x,
                                          _data.robot[i].y, _data.robot[i].line_speed_x,
                                          _data.robot[i].line_speed_y, j, _data.robot[j].towards, _data.robot[j].x,
                                          _data.robot[j].y, _data.robot[j].line_speed_x,
                                          _data.robot[j].line_speed_y)


        # 发出指令
        # Data.log_print('======= %d =======' % _data.frame)
        # sys.stdout.write('%d\n' % _data.frame)
        # for i in range(4):
        #     if _data.current_works.list[i] is not None:
        #         task = _data.current_works.list[i]
        #         if task.state == 0:
        #             for j in range(i, 4):
        #                 if CheckCrush.CheckCrush(i, _data.robot[i].towards, _data.robot[i].x,
        #                                          _data.robot[i].y, j, _data.robot[j].towards, _data.robot[j].x,
        #                                          _data.robot[j].y) == 1:
        #                     sys.stdout.write('rotate %d %f\n' % (i, math.pi/4))
        #                     sys.stdout.write('rotate %d %f\n' % (j, -math.pi/4))
        #                     sys.stdout.write('forward %d %d\n' % (i, 4))
        #                     sys.stdout.write('forward %d %d\n' % (j, 4))
        #                 else:
        #                     Physics.doInstruct(i, _data.robot[i].node_id, -1, _data.robot[i].towards, _data.robot[i].x,
        #                                        _data.robot[i].y,
        #                                        task.start.id, task.start.x, task.start.y, task.state, _data.frame, task.end.type)
        #         else:
        #             for j in range(i, 4):
        #                 if CheckCrush.CheckCrush(i, _data.robot[i].towards, _data.robot[i].x,
        #                                          _data.robot[i].y, j, _data.robot[j].towards, _data.robot[j].x,
        #                                          _data.robot[j].y) == 1:
        #                     sys.stdout.write('rotate %d %f\n' % (i, math.pi/4))
        #                     sys.stdout.write('rotate %d %f\n' % (j, -math.pi/4))
        #                     sys.stdout.write('forward %d %d\n' % (i, 4))
        #                     sys.stdout.write('forward %d %d\n' % (j, 4))
        #                 else:
        #                     Physics.doInstruct(i, _data.robot[i].node_id, -1, _data.robot[i].towards, _data.robot[i].x,
        #                                        _data.robot[i].y,
        #                                        task.end.id, task.end.x, task.end.y, task.state, _data.frame, task.end.type)
        #     else:
        #         for j in range(i, 4):
        #             if CheckCrush.CheckCrush(i, _data.robot[i].towards, _data.robot[i].x,
        #                                      _data.robot[i].y, j, _data.robot[j].towards, _data.robot[j].x,
        #                                      _data.robot[j].y) == 1:
        #                 sys.stdout.write('rotate %d %f\n' % (i, math.pi/4))
        #                 sys.stdout.write('rotate %d %f\n' % (j, -math.pi/4))
        #                 sys.stdout.write('forward %d %d\n' % (i, 4))
        #                 sys.stdout.write('forward %d %d\n' % (j, 4))
        #             else:
        #                 Physics.doInstruct(i, -1, -1, _data.robot[i].towards, _data.robot[i].x, _data.robot[i].y,
        #                                    -1, _data.robot[i].x, _data.robot[i].y, -1, _data.frame, task.end.type)

        # 结束
        Data.finish()
