from antlr.CoolListener import CoolListener
from antlr.CoolParser import CoolParser
import asm
from structure import _allStrings, _methodsOffsets, _allInts, _methodsAsm
from structure import *

class TextListener(CoolListener):
    def __init__(self):
        self.labelN = 0
        self.formals = 0
        self.asms = {}
    
    def addLabel(self):
        self.labelN += 1
        return "label{}".format(self.labelN-1)
    
    def enterKlass(self, ctx:CoolParser.KlassContext):
        self.klass = ctx.getChild(1).getText()

    def enterMethod(self, ctx:CoolParser.MethodContext):
        self.formals = 0
        self.methodName = ctx.ID().getText()
    
    def enterFormal(self, ctx:CoolParser.FormalContext):
        self.formals += 1
    
    def exitMethod(self, ctx:CoolParser.MethodContext):
        nFormals = self.formals*4
        # TODO: Obtner locals
        nLocals = 0
        ts = (3+nLocals)*4
        expr = ""
        expr += asm.methodTpl_in.substitute(klass=self.klass, method=ctx.ID().getText(), ts=ts, fp=ts, s0=ts-4, ra=ts-8, locals=nLocals )
        expr += self.asms[ctx.expr()]
        expr += asm.methodTpl_out.substitute(ts=ts, fp=ts, s0=ts-4, ra=ts-8,formals=nFormals,locals=nLocals,everything=nFormals+ts)
        _methodsAsm.append(expr)
    
    def exitObject(self, ctx:CoolParser.ObjectContext):
        # TODO: Como se obtiene el address?
        address = "{}($fp)".format(12)
        expr = asm.varTpl.substitute(address=address, symbol=ctx.ID().getText(), klass=self.klass)
        self.asms[ctx] = expr
        ctx.asm = expr

    def exitInteger(self, ctx:CoolParser.IntegerContext):
        # Buscar literal
        literal = -1
        value = int(ctx.INTEGER().getText())
        for i in range(len(_allInts)):
            if _allInts[i] == value:
                literal = i
                break
        expr = asm.litTpl.substitute(literal="int_const{}".format(literal), value=value)
        self.asms[ctx] = expr
        ctx.asm = expr
    
    def exitString(self, ctx:CoolParser.StringContext):
        # Buscar literal
        literal = -1
        value = ctx.STRING().getText()[1:-1]
        for i in range(len(_allStrings)):
            if _allStrings[i] == value:
                literal = i
                break
        expr = asm.litTpl.substitute(literal="str_const{}".format(literal), value=value)
        self.asms[ctx] = expr
        ctx.asm = expr

    def exitBase(self, ctx: CoolParser.BaseContext):
        # Tenemos que considerar que todos los Primary son Base
        if hasattr(ctx.getChild(0), 'asm'):
            self.asms[ctx] = self.asms[ctx.getChild(0)]

    def enterEq(self, ctx:CoolParser.EqContext):
        ctx.label = self.addLabel()

    def exitEq(self, ctx:CoolParser.EqContext):
        exprLeft = self.asms[ctx.expr(0)]
        exprRight = self.asms[ctx.expr(1)]
        expr = asm.eqTpl.substitute(left_subexp=exprLeft, right_subexp=exprRight, label=ctx.label)
        self.asms[ctx] = expr

    def exitMult(self, ctx:CoolParser.MultContext):
        exprLeft = self.asms[ctx.expr(0)]
        exprRight = self.asms[ctx.expr(1)]
        expr = asm.arithTpl.substitute(left_subexp=exprLeft, right_subexp=exprRight, op="mul")
        self.asms[ctx] = expr

    def exitDiv(self, ctx:CoolParser.DivContext):
        exprLeft = self.asms[ctx.expr(0)]
        exprRight = self.asms[ctx.expr(1)]
        expr = asm.arithTpl.substitute(left_subexp=exprLeft, right_subexp=exprRight, op="div")
        self.asms[ctx] = expr
    
    def exitAdd(self, ctx:CoolParser.AddContext):
        exprLeft = self.asms[ctx.expr(0)]
        exprRight = self.asms[ctx.expr(1)]
        expr = asm.arithTpl.substitute(left_subexp=exprLeft, right_subexp=exprRight, op="add")
        self.asms[ctx] = expr

    def exitSub(self, ctx:CoolParser.SubContext):
        exprLeft = self.asms[ctx.expr(0)]
        exprRight = self.asms[ctx.expr(1)]
        expr = asm.arithTpl.substitute(left_subexp=exprLeft, right_subexp=exprRight, op="sub")
        self.asms[ctx] = expr
    
    def exitParens(self, ctx:CoolParser.ParensContext):
        ctx.asm = self.asms[ctx.expr()]
        self.asms[ctx] = self.asms[ctx.expr()]

    def enterIf(self, ctx:CoolParser.IfContext):
        ctx.label_false = self.addLabel()
        ctx.label_exit = self.addLabel()

    def exitIf(self, ctx:CoolParser.IfContext):
        exprTest = self.asms[ctx.expr(0)]
        exprTrue = self.asms[ctx.expr(1)]
        exprFalse = self.asms[ctx.expr(2)]
        expr = asm.ifTpl.substitute(test_subexp=exprTest, true_subexp=exprTrue, false_subexp=exprFalse, label_false=ctx.label_false, label_exit=ctx.label_exit)
        self.asms[ctx] = expr
    
    def enterCall(self, ctx:CoolParser.CallContext):
        ctx.label = self.addLabel()        

    def exitCall(self, ctx:CoolParser.CallContext):
        expr = ""
        # TODO: Checar el tipo de call
        expr += asm.callParametersTpl.substitute(exp=self.asms[ctx.expr(0)])
        expr += asm.selfStr
        line = ctx.start.line
        expr += asm.callTpl1.substitute(fileName='str_const0', line=line, label=ctx.label)
        off = _methodsOffsets["{}.{}".format(self.klass, ctx.ID().getText())] * 4
        expr += asm.callTpl_instance.substitute(off=off, offset=off//4, method=ctx.ID().getText())
        self.asms[ctx] = expr

    def exitBlock(self, ctx:CoolParser.BlockContext):
        expr = ""
        for e in ctx.expr():
            expr += self.asms[e]
        self.asms[ctx] = expr