from antlr.CoolListener import CoolListener
from antlr.CoolParser import CoolParser
from structure import *

class DataListener(CoolListener):
    # def __init__(self, klasses):
        # self.klasses = klasses
    
    def enterKlass(self, ctx:CoolParser.KlassContext):
        name = ctx.getChild(1).getText()
        inherits = "Object"
        if ctx.getChild(2).getText() == 'inherits':
            inherits = ctx.getChild(3).getText()
        self.klass = Klass(name=name, inherits=inherits)

    def enterString(self, ctx:CoolParser.StringContext):
        # _allStrings.append()
        print(ctx.STRING())