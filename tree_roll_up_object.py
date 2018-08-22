# We want the feature of measuring the RRAO for each portfolio and business line. A similar optionality with
# the tree.py script. Since this feature seems to be independent of the RRAO project and it seems to be used
# in different objects, we created a data structure (as an abstract class in Python) to generalize this feature.
# This data structure has a tree structure that it needs to take an input for the nodes of the tree. After
# calculating the values for each leaf it rolls it up to all the nodes. In this specific project the values are
# just a number representing the RRAO measure, in another project it can be a DataFrame, or any other Python object.
# In order to be used in other project, we just have to specify how to get the values for the leaves and how the
# values pass from Children to parents, everything else has been already implemented.

from collections import deque
from abc import ABC, abstractmethod, ABCMeta


class Node(object):
    def __init__(self, name):
        self.name = name
        self.value = None
        self.parent = None
        self.children = None

    def __str__(self):
        if self.parent is None:
            parent = 'None'
            parent = str(self.parent.name)
        if self.children is None:
            children = 'None'
        else:
            children = []
            for child in self.children:
                children.append(child.name)
        return "{}(parent= {}, children = {}, value = {})".format(self.name, parent, str(children), self.value)

    def add_child(self, child):
        if self.children is None:
            self.children = [child]
        else:
            self.children.append(child)
        child.parent = self


class AbstractTree(metaclass=ABCMeta):
    """This is an abstract class. The goal of this class is to put the basic building blocks for creating a Tree data
    structure from a file. We assume that the input file is of the form: every line consist of <parent>, <child_1>, ..., 
    <child_N>. The additional feature of this data structure is that information gathered at the leaf level should be 
    passed and proceeded by upper level all the way to the root."""

    # When you use this class, you should include the first line to __init__ function to be:
    # super().__init__(<tree_structure_file>)
    def __init__(self, tree_structure_file, requested_node=None, print_upto_depth=None, excel_friendly=False):
        self.root = None
        self.print_upto_depth = print_upto_depth
        self.requested_node = requested_node
        self.excel_friendly = excel_friendly
        # We assume that the tree is small enough that all nodes fit into a dictionary.
        self.current_tree_nodes = {}
        self.leaves = set()
        self.build_tree(tree_structure_file)
        # The __init__ of the final class should start with:
        # super().__init__(user_input_object.tree_structure_file, user_input_object.portfolio, user_input_object.depth)
        #  and finish with:
        # self.calculate_value_leaf_nodes()
        # self.calculate_values()

    def __str__(self):
        if self.requested_node is None:
            stack = deque([(self.root, 0)])
        else:
            stack = deque([(self.requested_node, 0)])
        list_print_tuples = []
        max_node_name = 0

        while stack:
            current_tuple = stack.popleft()
            current_node = current_tuple[0]
            level = current_tuple[1]
            if self.excel_friendly is True:
                level_indicator = (level * '___') + current_node.name
            else:
                level_indicator = (level * '---') + current_node.name
            if self.print_upto_depth is None or self.print_upto_depth >= level:
                list_print_tuples.append((level_indicator, current_node.value))
                if len(level_indicator) > max_node_name and current_node.value != 0:
                    max_node_name = len(level_indicator)
                if current_node.children is not None:
                    for child in current_node.children[::-1]:
                        stack.appendleft((child, level+1))

        if self.excel_friendly is True:
            out_string = ",RRAO\n"
            output_format = "{},{}\n"
            num_format = "{}"
        else:
            out_string = ("{:" + str(max_node_name+1) + "}{:>20}\n").format("", "RRAO")
            output_format = "{:" + str(max_node_name+1) + "}{:.>20}\n"
            num_format = "{:,}"

        for node_name, value in list_print_tuples:
            if value != 0:
                value_string = num_format.format(round(value, 2))
                out_string += output_format.format(node_name, value_string)
        return out_string[:-1]  # It deletes the last character which is '\n'

    def build_tree(self, path_of_tree_file):
        with open(path_of_tree_file, 'r') as file:
            for line in file:
                line = line.replace('\n', '')
                node_name = line.split(',')[0]
                if node_name not in self.current_tree_nodes:
                    self.current_tree_nodes[node_name] = Node(node_name)
                if self.requested_node == node_name:
                    self.requested_node = self.current_tree_nodes[node_name]
                current_node = self.current_tree_nodes[node_name]
                if current_node in self.leaves:
                    self.leaves.remove(current_node)
                for child in line.split(',')[1:]:
                    if child not in self.current_tree_nodes:
                        self.current_tree_nodes[child] = Node(child)
                        self.leaves.add(self.current_tree_nodes[child])
                    current_node.add_child(self.current_tree_nodes[child])
                # We assume that the root is denoted by the line: None,root
                if node_name == 'None':
                    self.root = self.current_tree_nodes[line.split(',')[1]]
                    self.current_tree_nodes[line.split(',')[1]].parent = None

    def calculate_values(self):
        last_evaluated_tree_level = set(self.leaves)
        while last_evaluated_tree_level != {self.root}:
            for evaluated_node in last_evaluated_tree_level:
                if set(evaluated_node.parent.children) <= last_evaluated_tree_level:  # Checks for if it is a subset
                    evaluated_node.parent.value = self.roll_up_one_step(evaluated_node.parent)
                    last_evaluated_tree_level -= set(evaluated_node.parent.children)
                    last_evaluated_tree_level.add(evaluated_node.parent)
                    break

    @abstractmethod
    def calculate_value_leaf_nodes(self):
        # It is a void function, it just evaluates the value attribute in each node.
        pass

    @abstractmethod
    def roll_up_one_step(self):
        # It is a non-void function. It returns the value that the parent should have.
        return None
