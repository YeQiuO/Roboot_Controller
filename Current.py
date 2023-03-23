class Current:

    def __init__(self):
        self.list = [None, None, None, None]
        self.wait = 4
        self.remain_distance = [9999, 9999, 9999, 9999]

    # def b(self):
    #     for i in [self.a, self.remain_distance]:
    #         i[0] = 1


if __name__ == '__main__':
    # temp = [1, 2, 3, 4, 5, 6]
    temp = [[1, 2], [3, 4], [5, 6]]
    i = temp[:2]
    print(i)

