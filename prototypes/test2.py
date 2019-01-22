import ast
import inspect
import operator

class Node:
    def __init__(self, op, left, right):
        self.op = op.__class__.__name__
        lname = left.__class__.__name__
        rname = right.__class__.__name__

        self.lval = None
        self.lnode = None
        self.rval = None
        self.rnode = None
        self.out = None

        if lname == "Num":
            self.lval = left.n
        if lname == "BinOp":
            self.lnode = left
        if rname == "Num":
            self.rval = right.n
        if rname == "BinOp":
            self.rnode = left

        self.next = None
        self.back_left = None
        self.back_right = None

    def forward(self):
        if self.lval != None and self.rval != None:
            if self.op == "Add":
                self.out = self.lval + self.rval

            if self.op == "Mult":
                self.out = self.lval * self.rval

            if self.op == "Sub":
                self.out = self.lval - self.rval

            if self.op == "Div":
                self.out = self.lval / self.rval

input = '(a + b) * (b + 1)'

tree = ast.parse(input).body[0].value

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
    node.forward()
    if lnode is not None:
        node.lnode = lnode
        node.lval = lnode.out
    if rnode is not None:
        node.rnode = rnode
        node.rval = rnode.out
    node.forward()
    return node

node1 = gen_calc_graph(tree)

print(node1.lval)
print(node1.rnode.lval)
print(node1.rnode.rval)
print(node1.out)
