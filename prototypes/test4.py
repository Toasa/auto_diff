# astを下からたどって、計算グラフを生成し、
# 上(root node)から下に向かって辿ることで、back-propagationを行う

import ast
import inspect
import operator
import sys
from math import *

class Var:
    def __init__(self, name, val, is_imm=False):
        self.name = name
        self.val = val
        self.dval = 0
        self.is_imm = is_imm
        self.parent_op = None
        vars[name] = self

# var: クラスVarのインスタンス
# val: 実数値
class Op:
    def __init__(self, op, lvar, rvar):
        self.op = op
        self.lvar = lvar
        self.rvar = rvar
        self.outvar = None

    def forward(self):
        global var_count

        lval = self.lvar.val
        rval = self.rvar.val

        outval = None

        if self.op == "Add":
            outval = lval+ rval

        if self.op == "Mult":
            outval = lval * rval

        if self.op == "Sub":
            outval = lval - rval

        if self.op == "Div":
            outval = lval / rval

        var_name = "var" + str(var_count)
        var_count += 1
        outvar = Var(var_name, outval)
        outvar.parent_op = self
        self.outvar = outvar
        return outvar

    def backward(self):
        dval = self.outvar.dval
        lval = self.lvar.val
        rval = self.rvar.val

        if self.op == "Add":
            self.lvar.dval += dval
            self.rvar.dval += dval

        if self.op == "Mult":
            self.lvar.dval += dval * rval
            self.rvar.dval += dval * lval

        if self.op == "Sub":
            self.lvar.dval += dval
            self.rvar.dval -= dval

        if self.op == "Div":
            self.lvar.dval += dval * (1 / rval)
            self.rvar.dval += dval * (-lval / (rval * rval))

class Func:
    def __init__(self, func):
        self.func = func
        self.val = None

# 変数を格納する辞書
idents = {}
vars = {}
var_count = 0
imm_count = 0

# 逆伝播
def back_prop(var):
    var.parent_op.backward()
    if var.parent_op.lvar.parent_op != None:
        back_prop(var.parent_op.lvar)
    if var.parent_op.rvar.parent_op != None:
        back_prop(var.parent_op.rvar)

def gen_imm_var(tree):
    global imm_count
    imm_name = "imm" + str(imm_count)
    imm_count += 1
    var = Var(imm_name, tree.n, is_imm=True)
    return var

def walk(node):
    assert node.__class__.__name__ == "BinOp", "invalid ast class"
    opname = node.op.__class__.__name__

    lname = node.left.__class__.__name__
    rname = node.right.__class__.__name__

    lvar = None
    rvar = None

    if lname == "Num":
        lvar = gen_imm_var(node.left)
    elif lname == "Name":
        lvar = vars[node.left.id]
    elif lname == "BinOp":
        lvar = walk(node.left)

    if rname == "Num":
        rvar = gen_imm_var(node.right)
    elif rname == "Name":
        rvar = vars[node.right.id]
    elif rname == "BinOp":
        rvar = walk(node.right)

    op = Op(opname, lvar, rvar)
    outvar = op.forward()
    return outvar

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
        lval = idents[tree.left.id]
    if rname == "Num":
        rval = tree.right.n
    if rname == "Name":
        rval = idents[tree.right.id]

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

def gen_var(trees, print_info=False):
    for node in trees.body:
        if print_info:
            print("-" * 50)
            print(node.__class__.__name__)
            print(ast.dump(node))
        if node.__class__.__name__ == "Assign":
            if node.value.__class__.__name__ == "Num":
                num = node.value.n
            elif node.value.__class__.__name__ == "Name":
                num = idents[node.value.id]
            elif node.value.__class__.__name__ == "BinOp":
                num = solve_var(node.value)
            else:
                print("unknown variable:")
                exit()
            for target in node.targets:
                idents[target.id] = num
                Var(target.id, num)
        if node.__class__.__name__ == "Expr":
            walk(node.value)


def main():

    input = """
a = 6
b = 4
c = 1 + b
(a + b) * (b + c)"""

# forward-modeからやるので、変数の値は定まっているものとできる
#
    tree = ast.parse(input)

    root_node = gen_var(tree, True)

    root_var = vars["var" + str(var_count - 1)]

    root_var.dval = 5

    back_prop(root_var)
    print(vars["a"].dval)
    print(vars["b"].dval)
    print(vars["c"].dval)

if __name__ == "__main__":
    main()
