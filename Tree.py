class Tree:

    # pattern 0：Key Node 7
    def __init__(self, node, pattern):
        self.node = node  # [7, 8/9]
        self.pattern = pattern

        # self.son6 = None
        # self.son5 = None
        # self.son4 = None
        # self.father = None

        self.sons = None
        self.super_sons = None

        # self.appoint = []

    def update_0(self, super_sons, sons):
        self.super_sons = super_sons
        self.sons = sons

    # pattern 1：Key Node 9
    def update_1(self, sons):
        self.sons = sons
