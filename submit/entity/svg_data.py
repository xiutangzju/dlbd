# -*- coding: UTF-8 -*-
# 表节点类
class Node:
    node_type = {
        "table": 0,
        "column": 1
    }

    """
    node_type: 1->column, 0->table
    """
    def __init__(self, id, name, group, data_type, node_type=1):
        self.id = id
        self.name = name
        self.group = group
        self.data_type = data_type
        self.node_type = node_type
        self.highlight = True

    def is_equal(self, node):
        if self.name == node.name:
            return True
        else:
            return False


# 表类
class Table:
    def __init__(self, name, nodes=None):
        self.name = name
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

    def is_include(self, node):
        is_in = False
        for cur_node in self.nodes:
            if cur_node.is_equal(node):
                is_in = True
                break
        return is_in


# 连接类
class IntraLink:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.type = "Table-to-Column"
        self.link_type = 0
        self.highlight = True


class ExternalLink:
    def __init__(self, source, target, source_group, target_group):
        self.source = source
        self.target = target
        self.source_group = source_group
        self.target_group = target_group
        self.type = "Table-to-Table"
        self.link_type = 1
        self.highlight = True


# 图连接类
class SchemaGraphLink:
    def __init__(self, source, target, value):
        self.source = source
        self.target = target
        self.value = value


class SearchSpaceLink:
    def __init__(self, source, target, type, status=1):
        self.source = source
        self.target = target
        self.type = type
        self.status = status


# 图数据类
class Data:
    def __init__(self, nodes, links):
        self.nodes = nodes
        self.links = links
