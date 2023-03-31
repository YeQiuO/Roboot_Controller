import sys

from map3 import Data, Physics
from map3.Task import Task


def run3():
    # 初始化
    _data = Data.Data()
    # count = _data.load()
    physics = Physics.Physics()

    while True:
        Data.log_print('======= %d =======' % _data.frame)
        # 接收、处理数据、调度
        _data.update()

        # 发出指令
        sys.stdout.write('%d\n' % _data.frame)
        for i in range(4):
            if _data.current_works.list[i] is not None:
                task = _data.current_works.list[i]
                if task.state == 0:
                    physics.doInstruct(i, _data.robot[i].node_id, _data.robot[i].towards, _data.robot[i].x,
                                       _data.robot[i].y, _data.robot[i].angle_speed, _data.robot[i].line_speed_x,
                                       _data.robot[i].line_speed_y,
                                       task.start.id, task.start.x, task.start.y, task.state,
                                       _data.current_works, _data.robot, _data.node_ids)
                else:
                    physics.doInstruct(i, _data.robot[i].node_id, _data.robot[i].towards, _data.robot[i].x,
                                       _data.robot[i].y, _data.robot[i].angle_speed, _data.robot[i].line_speed_x,
                                       _data.robot[i].line_speed_y,
                                       task.end.id, task.end.x, task.end.y, task.state,
                                       _data.current_works, _data.robot, _data.node_ids)
            else:
                physics.doInstruct(i, -1, _data.robot[i].towards, _data.robot[i].x, _data.robot[i].y,
                                   _data.robot[i].angle_speed, _data.robot[i].line_speed_x, _data.robot[i].line_speed_y,
                                   -1, _data.robot[i].x, _data.robot[i].y, -1,
                                   _data.current_works, _data.robot, _data.node_ids)

        if 2908 < _data.frame < 2930:
            sys.stdout.write('forward %d %d\n' % (3, 6))
            sys.stdout.write('rotate %d %f\n' % (3, 0))
        elif _data.frame == 8598:
            _data.current_works.list[0] = Task(_data.node_ids[42], _data.node_ids[41])
        elif _data.frame == 8619:
            _data.current_works.list[3] = Task(_data.node_ids[12], _data.node_ids[24])

        # 结束
        Data.finish()
