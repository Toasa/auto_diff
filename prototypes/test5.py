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
        self.parent_func = None
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
    def __init__(self, func, in_var):
        self.func = func
        self.in_var = in_var
        self.out_var = None
    def forward(self):
        global var_count

        outval = None
        if self.func == "sin":
            outval = sin(self.in_var.val)

        var_name = "var" + str(var_count)
        var_count += 1
        outvar = Var(var_name, outval)
        outvar.parent_func = self
        self.out_var = outvar
        return outvar

    def backward(self):
        out_val = self.out_var.dval

        if self.func == "sin":
            self.in_var.dval += cos(out_val)

# 変数を格納する辞書
idents = {}
vars = {}
var_count = 0
imm_count = 0

# 逆伝播
def back_prop(var):
    if var.parent_op != None:
        var.parent_op.backward()
        back_prop(var.parent_op.lvar)
        back_prop(var.parent_op.rvar)
    if var.parent_func != None:
        var.parent_func.backward()
        back_prop(var.parent_func.in_var)

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
    elif lname == "Call":
        arg_type = node.left.args[0].__class__.__name__
        if arg_type == "Name":
            f = Func(node.left.func.id, vars[node.left.args[0].id])
            lvar = f.forward()
        elif arg_type == "BinOp":
            in_var = walk(node.left.args[0])
            f = Func(node.left.func.id, in_var)
            lvar = f.forward()


    if rname == "Num":
        rvar = gen_imm_var(node.right)
    elif rname == "Name":
        rvar = vars[node.right.id]
    elif rname == "BinOp":
        rvar = walk(node.right)
    elif rname == "Call":
        arg_type = node.right.args[0].__class__.__name__
        if arg_type == "Name":
            f = Func(node.right.func.id, vars[node.right.args[0].id])
            rvar = f.forward()
        elif arg_type == "BinOp":
            in_var = walk(node.right.args[0])
            f = Func(node.right.func.id, in_var)
            rvar = f.forward()

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
(a * b) + sin(a)
"""

# forward-modeからやるので、変数の値は定まっているものとできる
#
    tree = ast.parse(input)

    root_node = gen_var(tree, True)

    root_var = vars["var" + str(var_count - 1)]

    root_var.dval = 5

    back_prop(root_var)
    print(root_var.val)
    print(vars["a"].dval)
    print(vars["b"].dval)

if __name__ == "__main__":
    main()
