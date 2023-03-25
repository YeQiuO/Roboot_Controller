class Task:

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.state = 0

    def detail(self):
        return str(self.start.id) + "----" + str(self.end.id) + '=====' + str(self.start.x) + "----" + str(
            self.start.y) + '=====' + str(self.end.x) + "----" + str(self.end.y)
