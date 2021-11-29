from antlr.CoolListener import CoolListener
from antlr.CoolParser import CoolParser
import asm
from structure import _allStrings, _allClasses, _allInts, _allExpr
from structure import *

class TextListener(CoolListener):
    def __init__(self, asms={}):
        self.labelN = 0
        self.asms = asms
    
    def addLabel(self):
        self.labelN += 1
        return "label{}".format(self.labelN-1)
    
    def enterKlass(self, ctx:CoolParser.KlassContext):
        self.klass = ctx.getChild(1).getText()

    def enterMethod(self, ctx:CoolParser.MethodContext):
        self.curr = ""
        self.methodName = ctx.ID().getText()
    
    def exitMethod(self, ctx:CoolParser.MethodContext):
        ts = (3+0)*4
        expr = ""
        expr += asm.methodTpl_in.substitute(klass=self.klass, method=ctx.ID().getText(), ts=ts, fp=ts, s0=ts-4, ra=ts-8, locals=0 )
        # TODO: Qué es formals y locals?
        expr += self.asms[ctx.expr()]
        expr += asm.methodTpl_out.substitute(ts=ts, fp=ts, s0=ts-4, ra=ts-8,formals=4,locals=ts,everything=ts+4)
        print(expr)
    
    def enterObject(self, ctx:CoolParser.ObjectContext):
        # TODO: Como se obtiene el address?
        expr = asm.varTpl.substitute(address="{}($fp)".format(12), symbol=ctx.ID().getText(), klass=self.klass)
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
    
    def exitCall(self, ctx:CoolParser.CallContext):
        # TODO: Borrar este if
        if self.methodName != "fact": return
        expr = ""
        # TODO: Check wich call case is
        expr += asm.callParametersTpl.substitute(exp=self.asms[ctx.expr(0)])
        expr += asm.callStr1
        # TODO: Definir la linea de la llamada en el programa
        line = 7
        expr += asm.callTpl1.substitute(fileName='str_const0', line=line, label=self.addLabel())
        # TODO: Cómo se obtiene off?
        off = 28
        expr += asm.callTpl_instance.substitute(off=off, offset=off/4, method=ctx.ID().getText())
        self.asms[ctx] = expr

    



    def exitBlock(self, ctx:CoolParser.BlockContext):
        expr = "Block"
        self.asms[ctx] = expr