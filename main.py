import ast
from math import *

# 演算子クラス(Op)や関数クラス(Func)の入力と出力となる。
# Varクラスのインスタンスはnameを持ち、グローバルな辞書vars内に、
# nameをキーに、自分自身を値として、登録する。
class Var:
    def __init__(self, name, val, is_imm=False):
        self.name = name
        self.val = val # forward方向への出力値
        self.dval = 0 # backward方向への出力値
        self.is_imm = is_imm
        self.parent_op = None
        self.parent_func = None
        vars[name] = self

# Varクラスの2つのインスタンスである、lvar, rvarから、
# 演算子opでoutvarを生成する
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

# Funcクラスのインスタンスである invarから、１つのoutvarを生成する
class Func:
    def __init__(self, func, invar):
        self.func = func
        self.invar = invar
        self.outvar = None

    def forward(self):
        global var_count

        outval = None
        if self.func == "sin":
            outval = sin(self.invar.val)
        if self.func == "cos":
            outval = cos(self.invar.val)
        if self.func == "exp":
            outval = exp(self.invar.val)
        if self.func == "log":
            outval = log(self.invar.val)
        if self.func == "relu":
            if self.invar.val > 0:
                outval = self.invar.val
            else:
                outval = 0
        if self.func == "sigmoid":
            outval = 1 / (1 + exp(-self.invar.val))

        var_name = "var" + str(var_count)
        var_count += 1
        outvar = Var(var_name, outval)
        outvar.parent_func = self
        self.outvar = outvar
        return outvar

    def backward(self):
        outval = self.outvar.dval

        if self.func == "sin":
            self.invar.dval += outval * cos(self.invar.val)
        if self.func == "cos":
            self.invar.dval += outval * -sin(self.invar.val)
        if self.func == "exp":
            self.invar.dval += outval * exp(self.invar.val)
        if self.func == "log":
            assert outval != 0, "invalid operand"
            self.invar.dval += outval * (1 / self.invar.val)
        if self.func == "relu":
            if self.invar.val > 0:
                self.invar.dval += outval * self.invar.val
            else:
                self.invar.dval += 0
        if self.func == "sigmoid":
            self.invar.dval += outval * ((1 / (1 + exp(-self.invar.val))) * (1 / (1 + exp(-self.invar.val))) * exp(-self.invar.val))

# 識別子を格納する辞書
idents = {}
# 変数を格納する辞書
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
        back_prop(var.parent_func.invar)

# 即値用のvarを生成する
def gen_imm_var(tree):
    global imm_count
    imm_name = "imm" + str(imm_count)
    imm_count += 1
    var = Var(imm_name, tree.n, is_imm=True)
    return var

# 抽象構文木を渡り歩き、forward方向に計算を進める
def walk(node):
    n_name = node.__class__.__name__
    if n_name == "BinOp":
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
                invar = walk(node.left.args[0])
                f = Func(node.left.func.id, invar)
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
                invar = walk(node.right.args[0])
                f = Func(node.right.func.id, invar)
                rvar = f.forward()

        op = Op(opname, lvar, rvar)
        outvar = op.forward()
        return outvar
    elif n_name == "Call":
        arg_type = node.args[0].__class__.__name__
        if arg_type == "Name":
            f = Func(node.func.id, vars[node.args[0].id])
            return f.forward()
        elif arg_type == "BinOp":
            invar = walk(node.args[0])
            f = Func(node.func.id, invar)
            return f.forward()
    elif n_name == "Name":
        return vars[node.id]


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
    if lname == "BinOp":
        lval = solve_var(tree.left)

    if rname == "Num":
        rval = tree.right.n
    if rname == "Name":
        rval = idents[tree.right.id]
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
        # 式は一つしかないと仮定する
        if node.__class__.__name__ == "Expr":
            walk(node.value)

def main():

    back_dval = 5


#     input = """
# a = 6
# b = 4
# c = 2
# (a + b) * (b + c)
# """

#     input = """
# a = 6
# b = 3
# c = 4
# d = 5
# (a / b) * (c / d)
# """

#     input = """
# a = 6
# b = 4
# (a * b) + sin(a)
# """

#     input = """
# a = 6
# b = 4
# (a * b) + cos(a)
# """

#     input = """
# a = 6
# b = 4
# c = 2
# (a + b) * (log(b) + c)
# """

    input = """
a = 6
b = 4
cos(a * sin(a + b))
"""



# forward-modeからやるので、変数の値は定まっているものとできる
#
    tree = ast.parse(input)

    root_node = gen_var(tree, print_info=False)

    root_var = vars["var" + str(var_count - 1)]

    root_var.dval = back_dval

    back_prop(root_var)

    print("forward total val:", root_var.val)

    print("backward entry val:", back_dval)

    for ident in idents.keys():
        print("backward val of {0}: {1}".format(ident, vars[ident].dval))


if __name__ == "__main__":
    main()
