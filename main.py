import sys

import Data, Physics

if __name__ == '__main__':
    # 初始化
    _data = Data.Data()
    _data.load()
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

        # 结束
        Data.finish()
