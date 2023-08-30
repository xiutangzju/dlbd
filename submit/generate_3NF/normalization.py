# -*- coding: UTF-8 -*-
class Normalization:
    def __init__(self, column_list, FD_list, columns_match_list):
        self.column_list = column_list
        self.FD_list = FD_list
        self.columns_match_list = columns_match_list
        self.L = set()
        self.R = set()
        self.LR = set()
        self.N = set()
        self.candidate_list = []
        self.table_schema_list = []

    def remove_transfer_FD(self):
        """ 消除传递函数依赖 """
        # 1. 根据函数依赖式的右部分组
        FD_dict = dict()
        for FD in self.FD_list:
            if FD[1] in list(FD_dict.keys()):
                FD_dict[FD[1]].append(FD[0])
            else:
                FD_dict[FD[1]] = list()
                FD_dict[FD[1]].append(FD[0])

        # 2. 每个组分别判断是否存在传递函数依赖
        for key, values in FD_dict.items():
            FD_left_group = list(values)
            is_delete = [False] * len(FD_left_group)
            for i in range(len(FD_left_group))[::-1]:
                for j in range(len(FD_left_group))[::-1]:
                    if j == i:
                        continue

                    # FD_left_group[i]是X，FD_left_group[j]是Y
                    is_valid = True
                    for element in FD_left_group[j]:
                        if element in FD_left_group[i]:
                            continue
                        FD_tmp_list = [FD_left_group[i], element]
                        if FD_tmp_list not in self.FD_list:
                            is_valid = False
                            break

                    if is_valid:
                        if self.similarity(FD_left_group[j], key):
                            is_delete[i] = True
                        else:
                            is_delete[j] = True
                        break

            # 删除函数依赖
            for k in range(len(is_delete))[::-1]:
                # 若删的只剩最后一个，那么不论这最后一个是否标记为删除，都不能删
                if k == 0 and len(FD_left_group) == 1:
                    break
                if is_delete[k]:
                    self.FD_list.remove([FD_left_group[k], key])
                    del FD_left_group[k]

    def similarity(self, Y, z):
        """ 判断Y属性集和z属性是否在语义上有关联 """
        meaning_z = self.columns_match_list[ord(z) - ord('A')]
        is_similar = False
        threshold = 0.5
        for element in Y:
            meaning_e = self.columns_match_list[ord(element) - ord('A')]
            # 判断两个语义是否有一定的相似度
            len_e = len(meaning_e)
            for i in range(len_e):
                if i == 0:
                    cur_meaning = meaning_e
                else:
                    cur_meaning = meaning_e[:-i]
                if cur_meaning in meaning_z:
                    if (len(cur_meaning) / len_e) >= threshold:
                        is_similar = True
                    break

            if is_similar:
                break
        return is_similar

    """
    属性分类
    L, R, LR, N
    """

    def classify_attr(self):
        is_occur = [False] * len(self.column_list)

        # 1. 初步确定L，R
        for FD in self.FD_list:
            # 函数依赖式的右边
            self.R.add(FD[1])
            is_occur[ord(FD[1]) - ord('A')] = True

            # 函数依赖式左边
            for element in FD[0]:
                self.L.add(element)
                is_occur[ord(element) - ord('A')] = True

        # 2. 从L，R中生成LR
        for element in self.L:
            if element in self.R:
                self.LR.add(element)
                self.R.remove(element)
        for element in self.LR:
            self.L.remove(element)

        # 3. 生成N
        for i, occur in enumerate(is_occur):
            if not occur:
                self.N.add(chr(i + ord('A')))
                del self.column_list[i]

    """
    闭包算法
    """

    def compute_closure(self, candidate_list):
        is_add = True
        closure_set = set(candidate_list[:])

        # 当有新元素添加时
        while is_add:
            is_add = False
            subset_list = self.get_subset(sorted(list(closure_set)))

            for cur_set in subset_list:
                for FD in self.FD_list:
                    if cur_set == FD[0] and FD[1] not in closure_set:
                        closure_set.add(FD[1])
                        is_add = True
        return closure_set

    """
    计算集合的所有非空子集
    """

    def get_subset(self, universal_set):
        subset_list = universal_set[:]
        cur_layer = subset_list[:]
        while cur_layer:
            next_layer = self.get_next_layer(cur_layer)
            cur_layer = next_layer[:]
            for element in cur_layer:
                subset_list.append(element)
        return subset_list

    """
    当前层两两组合，得到下一层
    """

    def get_next_layer(self, cur_layer):
        next_layer = []
        for i in range(len(cur_layer)):
            for j in range(i + 1, len(cur_layer)):
                if cur_layer[i] != cur_layer[j] and cur_layer[i][0: -1] == cur_layer[j][0: -1]:
                    next_layer.append(cur_layer[i] + cur_layer[j][-1])
        return next_layer

    """
    寻找候选码
    """

    def compute_candidate(self):
        original_candidates = list(self.L)
        add_candidate_list = sorted(list(self.LR))

        # 判断self.L是否就是候选码
        cur_closure = self.compute_closure(original_candidates)
        cur_closure = sorted(list(cur_closure))
        if cur_closure == self.column_list:
            return original_candidates

        # 逐层逐个添加LR中的属性
        while add_candidate_list:
            for i in range(0, len(add_candidate_list))[::-1]:
                cur_candidates = sorted(original_candidates + list(add_candidate_list[i]))
                # 判断候选码的闭包是否为全集
                cur_closure = self.compute_closure(cur_candidates)
                cur_closure = sorted(list(cur_closure))
                if cur_closure == self.column_list:
                    self.candidate_list.append(set(cur_candidates))
                    # 候选码的真子集不能也是候选码
                    del add_candidate_list[i]

            if add_candidate_list:
                add_candidate_list = self.get_next_layer(add_candidate_list)

    """
    分解得到符合3NF的表结构
    """

    def normalization(self):
        # 去除传递函数依赖
        self.remove_transfer_FD()
        print(self.FD_list)
        # 属性分类
        self.classify_attr()
        # 得到候选码
        self.compute_candidate()

        # 为函数依赖分组
        same_left_dict = dict()
        for FD in self.FD_list:
            if FD[0] in list(same_left_dict.keys()):
                same_left_dict[FD[0]].append(FD[1])
            else:
                same_left_dict[FD[0]] = list(FD[1])

        # 分解表结构
        for keys, vals in same_left_dict.items():
            cur_table = set()
            for key in keys:
                cur_table.add(key)
            for val in vals:
                cur_table.add(val)
            self.table_schema_list.append(cur_table)
        self.table_schema_list += self.candidate_list

        # 去掉表结构中的重复元素
        self.remove_duplicate()

    """
    去掉表结构中的重复
    """

    def remove_duplicate(self):
        for i in range(len(self.table_schema_list))[::-1]:
            for j in range(i + 1, len(self.table_schema_list))[::-1]:
                if self.table_schema_list[i] <= self.table_schema_list[j]:
                    del self.table_schema_list[i]
                    break
                elif self.table_schema_list[j] <= self.table_schema_list[i]:
                    del self.table_schema_list[j]


if __name__ == '__main__':
    col_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    FD_list = [['AB', 'C'], ['AB', 'F'], ['AB', 'G'], ['AE', 'F'], ['AE', 'G'], ['AG', 'F'], ['ABE', 'D'], ['ABD', 'E'],
               ['ADG', 'E'], ['ACDE', 'B'], ['ACDG', 'B']]
    n = Normalization(col_list, FD_list)
    n.remove_transfer_FD()
    print(n.FD_list)
    # n.normalization()
    # print(len(n.table_schema_list))
    # print(n.table_schema_list)
