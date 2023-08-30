# -*- coding: UTF-8 -*-
from submit.entity.svg_data import Node, Table, IntraLink, ExternalLink


class GenerateTableSchema:
    def __init__(self, table_schema_list):
        self.table_schema_list = table_schema_list
        self.tables = list()
        self.intra_links = list()
        self.external_links = list()

    def generate_all(self):
        cur_id = 0
        cur_group = 1
        # 生成表结构和表内连接
        for i, table in enumerate(self.table_schema_list):
            cur_table_name = "t_" + str(i + 1)
            cur_table_nodes = list()
            cur_intra_links = list()
            cur_table_nodes.append(Node(cur_id, cur_table_name, cur_group, "none", Node.node_type.get("table")))
            table_node_id = cur_id
            cur_id += 1

            for node in list(table):
                cur_node = Node(cur_id, node[0], cur_group, node[1])
                cur_table_nodes.append(cur_node)
                cur_intra_links.append(IntraLink(table_node_id, cur_id))

                # 生成表外连接
                for j, former_table in enumerate(self.tables):
                    if former_table.is_include(cur_node):
                        self.external_links.append(
                            ExternalLink(former_table.nodes[0].id, table_node_id, j + 1, cur_group))
                        break

                cur_id += 1

            self.tables.append(Table(cur_table_name, cur_table_nodes))
            self.intra_links.append(cur_intra_links)
            cur_group += 1

    def generate_table(self):
        cur_id = 0
        cur_group = 1
        # 生成表结构和表内连接
        for i, table in enumerate(self.table_schema_list):
            cur_table_name = "t_" + str(i + 1)
            cur_table_nodes = list()
            cur_table_nodes.append(Node(cur_id, cur_table_name, cur_group, "none", Node.node_type.get("table")))
            cur_id += 1

            for node in list(table):
                cur_node = Node(cur_id, node[0], cur_group, node[1])
                cur_table_nodes.append(cur_node)
                cur_id += 1

            self.tables.append(Table(cur_table_name, cur_table_nodes))
            cur_group += 1