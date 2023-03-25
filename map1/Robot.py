class Robot:

    def __init__(self, id, node_id, thing_type, time, crash, angle_speed, line_speed_x, line_speed_y, towards, x, y):
        self.id = id
        self.node_id = node_id
        self.thing_type = thing_type
        self.time = time
        self.crash = crash
        self.angle_speed = angle_speed
        self.line_speed_x = line_speed_x
        self.line_speed_y = line_speed_y
        self.towards = towards
        self.x = x
        self.y = y
