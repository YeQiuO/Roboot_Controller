class Tree:

    # pattern 0：Key Node 7
    def __init__(self, node, pattern):
        self.node = node  # [7, 8/9]
        self.pattern = pattern

        self.super_sons = []
        self.sons = []
        self.grand_son = []

        self.super_relation = []  # [key_node_id, son_id]

    # pattern 1：Key Node 7
    def update_0(self, sons):
        # self.super_sons = super_sons
        self.sons = sons

    # pattern 1：Key Node 9
    def update_1(self, super_sons, sons, grand_sons):
        self.super_sons = super_sons
        self.sons = sons
        self.grand_son = grand_sons

    def insert_super_son(self, son_id, key_node_id, node_ids):
        if son_id == -1 or len(self.is_in_relation(key_node_id)) == 0:
            return

        son = node_ids(son_id)
        if son in self.sons:
            self.sons.remove(son)
            self.super_sons.append(son)
            self.super_relation.append([key_node_id, son_id])

    def update_super_son(self, key_node_id, vacancy_count, node_ids):
        son_ids = self.is_in_relation(key_node_id)
        for son_id in son_ids:
            son_type = node_ids(son_id).type
            if vacancy_count[son_type - 4] == 1:
                son = node_ids(son_ids)
                self.sons.append(son)
                self.super_sons.remove(son)
                self.super_relation.remove([key_node_id, son_id])



    def is_in_relation(self, key_node_id):
        son_ids = []
        for i in self.super_relation:
            if i[0] == key_node_id:
                son_ids.append(i[1])
        return son_ids



