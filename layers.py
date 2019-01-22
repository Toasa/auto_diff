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


        var_name = "var" + str(var_count)
        var_count += 1
        outvar = Var(var_name, outval)
        outvar.parent_func = self
        self.outvar = outvar
        return outvar

    def backward(self):
        out_val = self.outvar.dval

        if self.func == "sin":
            self.invar.dval += cos(out_val)
        if self.func == "cos":
            self.invar.dval -= sin(out_val)
        if self.func == "exp":
            self.invar.dval += exp(out_val)
        if self.func == "log":
            assert outval != 0, "invalid operand"
            self.invar.dval += 1 / out_val
