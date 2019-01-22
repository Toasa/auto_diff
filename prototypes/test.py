import ast
import inspect
import operator

class PrintNodeVisiter(ast.NodeVisitor):
    def visit(self, node):
        print(node)
        return super().visit(node)

class Node:
    def __init__(self, op, left, right):
        self.op = op.__class__.__name__

        if left.__class__.__name__ == "BinOp":
            self.left = None
        else:
            self.left = left.n

        if right.__class__.__name__ == "BinOp":
            self.right = None
        else:
            self.right = right.n
        self.out = None

    #  2
    # ---\   5
    #  3  + ---\
    # ---/      \
    #            \   45
    #  4          × ---
    # ---\   9  /
    #  5  + ---/
    # ---/

        self.next = None
        self.back_left = None
        self.back_right = None

    def forward(self):
        if self.left.__class__.__name__ == "int" and self.right.__class__.__name__ == "int":
            if self.op == "Add":
                self.out = self.left + self.right

            if self.op == "Mult":
                self.out = self.left * self.right

input = '2 * 8 + 3'

tree = ast.parse(input).body[0].value

#print(inspect.getmembers(Node))

#PrintNodeVisiter().visit(tree)

# for node in list(ast.walk(tree)):
#     print(ast.dump(node))

def tree_print(tree, tab):
    print((" " * tab) + "op:", tree.op.__class__.__name__)

    if tree.left.__class__.__name__ == "BinOp":
        print(" "*tab + "left:")
        tree_print(tree.left, tab + 4)
    else:
        print((" " * tab) + "left:", tree.left.n)

    if tree.right.__class__.__name__ == "BinOp":
        print(" "*tab + "right:")
        tree_print(tree.right, tab + 4)
    else:
        print((" " * tab) + "right:", tree.right.n)

# tree_print(tree, 0)

def gen_node(tree):
    node = Node(tree.op, tree.left, tree.right)
    return node

def gen_calc_graph(tree):
    lname = tree.left.__class__.__name__
    rname = tree.right.__class__.__name__

    lnode = None
    rnode = None

    if lname == "BinOp":
        lnode = gen_calc_graph(tree.left)
    if rname == "BinOp":
        rnode = gen_calc_graph(tree.right)

    node = gen_node(tree)
    if lnode is not None:
        node.left = lnode
    if rnode is not None:
        node.right = rnode
    node.forward()
    return node

node1 = gen_calc_graph(tree)
print(node1.left.__class__.__name__)
print(node1.op)
print(node1.right)
print(node1.left.out)
