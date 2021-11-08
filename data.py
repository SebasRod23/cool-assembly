from antlr.CoolListener import CoolListener
from antlr.CoolParser import CoolParser
from structure import _allStrings, _allClasses, _allInts
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
        s: str = ctx.STRING().getText()[1:-1]

        if _allStrings and s not in _allStrings:
            _allStrings.append(s)
    
    def enterInteger(self, ctx:CoolParser.IntegerContext):
        number =int(ctx.INTEGER().getText())

        if not _allInts: _allInts.append(number)
        elif number not in _allInts:
            _allInts.append(number)
    
    def exitProgram(self, ctx:CoolParser.ProgramContext):
        _allStrings.append('<basic_class>')
        _allStrings.extend([ klass for klass in _allClasses.keys()])
        _allStrings.append("")