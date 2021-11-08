from antlr.CoolLexer import *
from antlr.CoolParser import *
from antlr4 import *

from typecheck import Typecheck

def main(file):
    parser = CoolParser(CommonTokenStream(CoolLexer(FileStream(file))))
    tree = parser.program()

    walker = ParseTreeWalker()
    typecheck = Typecheck()
    walker.walk(typecheck, tree)

if __name__ == '__main__':
    main("test.cool")
