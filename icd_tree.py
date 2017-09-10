# this class parses the output from scraping the ICD taxonomy and finds the LCA and distance between two codes

import Node as n


class IcdTree(object):

    def __init__(self, input_file):
        self.nodes = []
        self.node_codes = []
        self.root = n.Node('root', 0)
        self.add_node(self.root)
        self.input_file = input_file

    def get_node(self, code):
        for node in self.nodes:
            node_code = node.code.replace("'", "").strip()
            if str(code) == node_code:
                return node

        return None

    # goes through the input file, finds the first line with the matching node and returns that line truncated from the
    # root to the node
    @staticmethod
    def build_path_for_node(node, input_lines):
        path = []
        regex = r'\\b' + node + r'\\b'
        for line in input_lines:
            line = line.replace('[', '')
            line = line.replace(']', '')
            line = line.replace('\n', '')
            line = line.replace("'", "")

            split_line = line.split(', ')

            if node in split_line:
                for item in split_line:
                    path.append(item)
                    if item == node:
                        break
                break
        return path

    def get_lca_exponential_distance(self, node1, node2):
        if node1 == node2:
            lca = node1
            dist = 0
            return lca, dist

        input_lines = open(self.input_file, 'r').readlines()
        path1 = self.build_path_for_node(node1, input_lines)
        path2 = self.build_path_for_node(node2, input_lines)

        if len(path1) > len(path2):
            longer_path = path1
            shorter_path = path2

        else:
            longer_path = path2
            shorter_path = path1

        lca = None
        level = 0
        for i, item in enumerate(shorter_path):
            try:
                if item == longer_path[i]:
                    lca = item
                    level = i
                    continue
                else:
                    break
            except IndexError:
                lca = longer_path[i-1]
        dist = pow(2, 5 - level - 1)
        return lca, dist


if __name__ == '__main__':
    tree = IcdTree('icd_tree.txt')
    ancestor, distance = tree.get_lca_exponential_distance('001', '003.21')








