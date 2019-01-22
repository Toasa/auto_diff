# できていないところ
# input = (a + b) * (b + 1)
# のように、同じ変数が複数回登場するときに、その都度、べつのnodeを生成してしまい、
# back-propagationがうまくいかない
# まず、順方向に計算をたどってから、逆方向へ微分を考えるべき

import ast
import inspect
import operator

class Node:
    def __init__(self, op, lnode, rnode, lval, rval):

        # forward
        self.op = op
        self.lnode = lnode
        self.rnode = rnode
        self.lval = lval
        self.rval = rval
        self.out_node = None
        self.out_val = None

        # backward
        self.dout_val = None
        self.dlval = None
        self.drval = None

    def forward(self):
        if self.lval != None and self.rval != None:
            if self.op == "Add":
                self.out_val = self.lval + self.rval

            if self.op == "Mult":
                self.out_val = self.lval * self.rval

            if self.op == "Sub":
                self.out_val = self.lval - self.rval

            if self.op == "Div":
                self.out_val = self.lval / self.rval

    # トップダウン型の自動微分
    def backward(self):
        if self.lval != None and self.rval != None:
            if self.op == "Add":
                self.dlval = self.dout_val
                self.drval = self.dout_val

            if self.op == "Mult":
                self.dlval = self.dout_val * self.rval
                self.drval = self.dout_val * self.lval

            if self.op == "Sub":
                self.dlval = self.dout_val
                self.drval = -self.dout_val

            if self.op == "Div":
                self.dlval = self.dout_val * (1 / self.rval)
                self.drval = self.dout_val * (-self.lval / (self.rval * self.rval))


        if self.lnode != None and self.rnode != None:
            self.lnode.dout_val = self.dlval
            self.rnode.dout_val = self.drval

def gen_node(op, lnode, rnode, lval, rval):
    node = Node(op, lnode, rnode, lval, rval)
    return node

# 計算グラフを生成する
def gen_calc_graph(tree):
    op = tree.op.__class__.__name__

    lname = tree.left.__class__.__name__
    rname = tree.right.__class__.__name__

    lnode = None
    rnode = None

    lval = None
    rval = None

    if lname == "BinOp":
        lnode = gen_calc_graph(tree.left)
    if rname == "BinOp":
        rnode = gen_calc_graph(tree.right)
    if lname == "Name":
        lval = vars[tree.left.id]
    if rname == "Name":
        rval = vars[tree.right.id]
    if lname == "Num":
        lval = tree.left.n
    if rname == "Num":
        rval = tree.right.n

    node = gen_node(op, lnode, rnode, lval, rval)
    node.forward()
    if lnode is not None:
        node.lnode = lnode
        node.lval = lnode.out_val
        lnode.out_node = node
    if rnode is not None:
        node.rnode = rnode
        node.rval = rnode.out_val
        rnode.out_node = node
    node.forward()
    return node

# 変数の値を確定させる
def solve_var(tree):
    lname = tree.left.__class__.__name__
    rname = tree.right.__class__.__name__

    res = None
    lval = None
    rval = None

    if lname == "Num":
        lval = tree.left.n
    if lname == "Name":
        lval = vars[tree.left.id]
    if rname == "Num":
        rval = tree.right.n
    if rname == "Name":
        rval = vars[tree.right.id]

    if lname == "BinOp":
        lval = solve_var(tree.left)
    if rname == "BinOp":
        rval = solve_var(tree.right)

    if tree.op.__class__.__name__ == "Add":
        return lval + rval
    if tree.op.__class__.__name__ == "Sub":
        return lval - rval
    if tree.op.__class__.__name__ == "Mult":
        return lval * rval
    if tree.op.__class__.__name__ == "Div":
        return lval / rval

# 逆伝播
def back_prop(node):
    node.backward()
    if node.lnode != None:
        back_prop(node.lnode)
    if node.rnode != None:
        back_prop(node.rnode)

# astを渡り歩き、変数を辞書に登録し、計算グラフを生成する関数を呼ぶ
def walk(tree, print_info = False):
    for node in tree.body:
        if print_info:
            print("-" * 50)
            print(node.__class__.__name__)
            print(ast.dump(node))
        if node.__class__.__name__ == "Assign":
            if node.value.__class__.__name__ == "Num":
                num = node.value.n
            elif node.value.__class__.__name__ == "Name":
                num = vars[node.value.id]
            elif node.value.__class__.__name__ == "BinOp":
                num = solve_var(node.value)
            else:
                print("unknown variable:")
                exit()
            for target in node.targets:
                vars[target.id] = num
        if node.__class__.__name__ == "Expr":
            root_node = gen_calc_graph(node.value)

    return root_node

# 変数を格納する辞書
vars = {}

def main():

    input = """
a = 6
b = 4
c = 3
d = c + 1
(a + b) * (c + d)"""

    tree = ast.parse(input)

    root_node = walk(tree, True)
    print(vars)

    print(root_node.out_val)

    root_node.dout_val = 2

    back_prop(root_node)

    print("++++++++++++++++++")

    print(root_node.lnode.dlval)
    print(root_node.lnode.drval)
    print(root_node.rnode.dlval)
    print(root_node.rnode.drval)

if __name__ == "__main__":
    main()
