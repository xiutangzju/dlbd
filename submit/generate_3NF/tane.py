# -*- coding: UTF-8 -*-
from collections import defaultdict
import numpy as np
import sys
import copy


class Tane:
    def __init__(self, dataset, total_tuples, column_list):
        # 读取文件并获取文件属性
        self.dataset = dataset
        self.total_tuples = total_tuples  # 总列数
        self.column_list = column_list  # 属性名数组
        self.column_max_len_list = []  # 每一列中数据长度的最大值

        # 用于生成剥离分区的表T
        self.table_t = ['NULL'] * self.total_tuples

        self.L0 = []
        """
        右方集字典集
        存储全集R中，可能依赖于集合X的所有属性
        键是集合X，值是可能依赖于该集合的所有属性列表
        """
        self.dict_c_plus = {'': self.column_list}  # 右方集字典集
        self.dict_partitions = {}  # 剥离分区

        self.final_FD_list = []

    # 等价类划分
    def divide_equivalence(self, seq):
        max_len = 0
        equal_dict = defaultdict(list)
        # 归纳属性列中数据值相同的行
        for i, item in enumerate(seq):
            if len(str(item)) > max_len:
                max_len = len(str(item))
            equal_dict[item].append(i)
        self.column_max_len_list.append(max_len)
        return ((key, locs) for key, locs in equal_dict.items()
                if len(locs) > 0)

    # 递归发现右方集
    def find_c_plus(self, x):
        cur_sets = []
        for a in x:
            if x.replace(a, '') in self.dict_c_plus.keys():
                tmp = self.dict_c_plus[x.replace(a, '')]
            else:
                tmp = self.find_c_plus(x.replace(a, ''))
            cur_sets.insert(0, set(tmp))
        # TODO: 此处和原算法不一样
        c_plus = list(set.intersection(*cur_sets))
        return c_plus

    """
    计算右方集
    此处完全是为了剪枝后做的修复工作
    证明可得，若不剪枝的话，之前层的c_plus的keys完全是元素的组合，当前层不会用到上一层不存在的组合
    只有当某一层剪枝后，其之后的第一层（可能）、第二层（一定）会受到这一层的影响，才需要重新计算
    """

    def compute_c_plus(self, x):
        if x == '':
            return self.column_list

        c_plus = []
        for a in self.column_list:
            for b in x:
                tmp = x.replace(a, '')
                tmp = tmp.replace(b, '')
                if not self.valid_FD(tmp, b):
                    c_plus.append(a)

        return c_plus

    """
    有效性测试
    对于函数依赖：y -> z
    首先计算属性集y对于隔离分区的参数
    然后计算y与z的并集，判断加入z之后，有没有细化y的隔离分区
    若两个参数相等，因为y与z的并集相当于是以y为基础，所以z的加入并没有细化隔离分区，
    要么y和z的分区一样，要么y的分区比z的分区粒度更小
    """

    def valid_FD(self, y, z):
        if y == '' or z == '':
            return False

        # y -> z
        ey = self.compute_E(y)
        eyz = self.compute_E(y + z)
        if ey == eyz:
            return True
        else:
            return False

    """
    误差计算
    相当于是计算属性集X对于隔离分区的一个参数
    通过这个参数，可以明确该属性集对应的所有数据的分布情况
    """

    def compute_E(self, x):
        count = 0  # 所有等价类的大小的和
        for i in self.dict_partitions[''.join(sorted(x))]:
            count += len(i)
        e = (count - len(self.dict_partitions[''.join(sorted(x))])) / float(self.total_tuples)
        return e

    # 计算函数依赖
    def compute_dependencies(self, layer):
        # 第一步，通过上一层计算该层的右方集
        for x in layer:
            cur_sets = []
            for a in x:
                if x.replace(a, '') in self.dict_c_plus.keys():
                    tmp = self.dict_c_plus[x.replace(a, '')]
                else:
                    tmp = self.compute_c_plus(x.replace(a, ''))
                    self.dict_c_plus[x.replace(a, '')] = tmp

                cur_sets.insert(0, set(tmp))
            self.dict_c_plus[x] = list(set.intersection(*cur_sets))

        # 第二步，找到最小函数依赖，并对CPlus剪枝：删掉已经成立的；去掉肯定不可能的
        for x in layer:
            for a in x:
                if a in self.dict_c_plus[x]:
                    # 若X\{A} -> A 函数依赖成立，引理3.1成立，证明此为最小函数依赖
                    if self.valid_FD(x.replace(a, ''), a):
                        self.final_FD_list.append([x.replace(a, ''), a])
                        self.dict_c_plus[x].remove(a)

                        """
                        剪掉肯定不可能的
                        由于X\{A} -> A函数成立，可得原本依赖于X的属性全部可以依赖于X\{A}，最小函数依赖已不成立
                        最小函数依赖中是可以存在传递函数依赖的
                        """
                        cur_cols = self.column_list[:]  # 深度拷贝
                        for j in x:
                            if j in cur_cols:
                                cur_cols.remove(j)

                        for b in cur_cols:
                            if b in self.dict_c_plus[x]:
                                self.dict_c_plus[x].remove(b)

    """
    超键检查
    若属性集X不存在隔离分区，说明该属性集X对应的数据没有两个或以上相同的元组，即说明属性集X是键
    """

    def check_super_key(self, x):
        if self.dict_partitions[x] == [[]] or self.dict_partitions[x] == []:
            return True
        else:
            return False

    # 修剪属性格
    def prune(self, layer):
        for x in layer:
            # 右方集修剪
            # 若没有可能依赖于X的属性，就删去该属性集
            if not self.dict_c_plus[x]:
                layer.remove(x)

            # 键修剪
            if self.check_super_key(x):
                tmp = self.dict_c_plus[x][:]
                # 1. 计算c_plus(X) \ X
                for i in x:
                    if i in tmp:
                        tmp.remove(i)
                # 2. 遍历c_plus(X) \ X中的属性
                for a in tmp:
                    cur_sets = []
                    # 3. 计算c_plus((X + A) \ {B})
                    for b in x:
                        if ''.join(sorted((x + a).replace(b, ''))) not in self.dict_c_plus.keys():
                            self.dict_c_plus[''.join(sorted((x + a).replace(b, '')))] = self.find_c_plus(
                                ''.join(sorted((x + a).replace(b, ''))))
                        cur_sets.insert(0, set(self.dict_c_plus[''.join(sorted((x + a).replace(b, '')))]))

                    # 4. 计算c_plus((X + A) \ {B})交集，判断a是否在其中
                    if a in list(set.intersection(*cur_sets)):
                        self.final_FD_list.append([x, a])

                if x in layer:
                    layer.remove(x)

    # 生成下一层
    def generate_next_layer(self, cur_layer):
        next_layer = []
        for i in range(0, len(cur_layer)):
            for j in range(i + 1, len(cur_layer)):
                # 判断两个是否属于同一个前缀块
                if (not cur_layer[i] == cur_layer[j]) and cur_layer[i][0: -1] == cur_layer[j][0: -1]:
                    x = cur_layer[i] + cur_layer[j][-1]

                    # 判断x是否可以被纳入到下一层中
                    is_valid = True
                    for a in x:
                        if x.replace(a, '') not in cur_layer:
                            is_valid = False
                            break
                    if is_valid:
                        next_layer.append(x)
                        self.stripped_product(x, cur_layer[i], cur_layer[j])

        return next_layer

    # 生成剥离分区
    def stripped_product(self, x, y, z):
        table_s = [''] * len(self.table_t)
        partition_y = self.dict_partitions[''.join(sorted(y))]
        partition_z = self.dict_partitions[''.join(sorted(z))]
        partition_x = []
        for i in range(len(partition_y)):
            for t in partition_y[i]:
                self.table_t[t] = i
            table_s[i] = ''
        for i in range(len(partition_z)):
            for t in partition_z[i]:
                if self.table_t[t] != 'NULL':
                    table_s[self.table_t[t]] = sorted(list(set(table_s[self.table_t[t]]) | set([t])))
            # 重置table_s，防止partition_y和partition_z中不同的类别混入其中
            for t in partition_z[i]:
                if self.table_t[t] != 'NULL' and len(table_s[self.table_t[t]]) >= 2:
                    partition_x.append(table_s[self.table_t[t]])
                if self.table_t[t] != 'NULL':
                    table_s[self.table_t[t]] = ''
        for i in range(len(partition_y)):
            for t in partition_y[i]:
                self.table_t[t] = 'NULL'
        self.dict_partitions[''.join(sorted(x))] = partition_x

    # 计算剥离分区
    def compute_singleton_partitions(self):
        for a in self.column_list:
            self.dict_partitions[a] = []
            for element in self.divide_equivalence(self.dataset[a].tolist()):
                if len(element[1]) > 1:
                    self.dict_partitions[a].append(element[1])

    """
    去掉重复的依赖
    比如：C -> A, C -> D, AD -> C
    比如：B -> C, C -> B，这种情况优先去掉C->B，因为B，C中B更有可能是语义上的ID
    """
    def remove_duplicate(self):
        # 找到FD中左边是单项的元素
        left_single_num = 0
        while left_single_num < len(self.final_FD_list) and \
                len(self.final_FD_list[left_single_num][0]) == 1:
            cur_FD = self.final_FD_list[left_single_num]
            # 若依赖式的左部大于右部，且它的反转依赖式已存在
            if cur_FD[0] > cur_FD[1] and cur_FD[::-1] in self.final_FD_list:
                del self.final_FD_list[left_single_num]
            else:
                left_single_num += 1
        left_single_list = self.final_FD_list[0: left_single_num]

        for i in range(left_single_num, len(self.final_FD_list))[::-1]:
            is_match = True
            for element in self.final_FD_list[i][0]:
                cur_reverse = [self.final_FD_list[i][1], element]
                if cur_reverse not in left_single_list:
                    is_match = False
                    break
            if is_match:
                del self.final_FD_list[i]

    # 主函数
    def main(self):
        L0 = []
        L1 = self.column_list[:]
        i = 1
        L = [L0, L1]
        self.compute_singleton_partitions()
        while L[i]:
            self.compute_dependencies(L[i])
            self.prune(L[i])
            tmp = self.generate_next_layer(L[i])
            L.append(tmp)
            i += 1

        self.remove_duplicate()
        # print(self.final_FD_list)

    def test(self):
        self.compute_singleton_partitions()
        # print("A", self.dict_partitions["A"])
        # print("C", self.dict_partitions["C"])
        # print("D", self.dict_partitions["D"])
        # print("E", self.dict_partitions["E"])

        self.stripped_product("BC", "B", "C")
        self.stripped_product("BD", "B", "D")
        # self.stripped_product("AE", "A", "E")
        # print("CD", self.dict_partitions["CD"])

        self.stripped_product("BCD", "BC", "BD")
        # self.stripped_product("ACE", "AC", "AE")
        # print("BCD", self.dict_partitions["BCD"])

        # self.stripped_product("ACDE", "ACD", "ACE")
        print("BCD", self.dict_partitions["BCD"])

        print("G", self.dict_partitions["G"])
