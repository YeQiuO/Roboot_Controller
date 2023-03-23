class Tree:

    # pattern 0：Key Node 7
    def __init__(self, node, pattern):
        self.node = node  # [7, 8/9]
        self.pattern = pattern

        self.super_sons = []
        self.sons = []
        self.grand_son = []

    # pattern 1：Key Node 7
    def update_0(self, super_sons, sons):
        self.super_sons = super_sons
        self.sons = sons

    # pattern 1：Key Node 9
    def update_1(self, sons, grand_sons):
        self.sons = sons
        self.grand_son = grand_sons
