from antlr4 import *
from antlr.CoolLexer import *
from antlr.CoolParser import *
from antlr.CoolListener import *

import sys
import math
from string import Template
import asm
from data import DataListener
from structure import _allStrings, _allInts, _allClasses
from structure import *

basicTags = dict(intTag=2, boolTag=3, stringTag=4)

class Output:
    def __init__(self):
        self.accum = ''

    def p(self, *args):
        '''
        Si tiene un argumento es una etiqueta
        '''
        if len(args) == 1:
            self.accum += '%s:\n' % args[0]
            return

        '''
        Si tiene más, indenta el primero y los demás los separa con espacios
        '''
        r = '    %s    ' % args[0]        
        for a in args[1:-1]:
            r += ' %s' % str(a)

        if type(args[-1]).__name__ != 'int' and args[-1][0] == '#':
            for i in range(64 - len(r)):
                r += ' '
        r += str(args[-1])

        self.accum += r + '\n'

    def out(self):
        return self.accum

def global_data(o):
        o.accum = asm.gdStr1 + asm.gdTpl1.substitute(basicTags) + asm.gdStr2

def constants(o):
    # Strings
    # TODO: Check special case for empty string
    for i in range(len(_allStrings)-1, -1, -1,):
        # Obtener tamaño del string
        strLen = len(_allStrings[i].replace("\\",""))

        # Obtener el tamaño del objeto 
        size = int(4+math.ceil((strLen+1)/4))
        
        # Guardar el tamaño del string dentro de las constantes Integer si no existe 
        if not strLen in _allInts:
            _allInts.append(strLen)
            index = len(_allInts)-1
        else:
            index = _allInts.index(strLen)

        o.accum += asm.cTplStr.substitute(idx=i, tag=basicTags['stringTag'], size=size, sizeIdx=index, value=_allStrings[i])
    
    # Integers
    for i in range(len(_allInts)-1, -1, -1,):
        o.accum += asm.cTplInt.substitute(idx=i, tag=basicTags['intTag'], value=_allInts[i])

    # Booleans
    o.accum += asm.boolStr.substitute(tag=basicTags['boolTag'])

def tables(o):
    """
    1. class_nameTab: tabla para los nombres de las clases en string
        1.1 Los objetos ya fueron generados arriba
        1.2 El tag de cada clase indica el desplazamiento desde la etiqueta class_nameTab
    2. class_objTab: prototipos (templates) y constructores para cada objeto
        2.1 Indexada por tag: en 2*tag está el protObj, en 2*tag+1 el init
    3. dispTab para cada clase
        3.1 Listado de los métodos en cada clase considerando herencia
"""
    #Ejemplo (REEMPLAZAR):

    o.p('class_nameTab')
    o.p('.word', 'str_const3')

    o.p('class_objTab')
    o.p('.word', 'Object_protObj')
    o.p('.word', 'Object_init') 

    o.p('Object_dispTab')
    o.p('.word', 'Object.abort')
    o.p('.word', 'Object.type_name')
    o.p('.word', 'Object.copy')
    
def templates(o):
    """
    El template o prototipo para cada objeto (es decir, de donde new copia al instanciar)
    1. Para cada clase generar un objeto, poner atención a:
        - nombre
        - tag
        - tamanio [tag, tamanio, dispTab, atributos ... ] = ?
            Es decir, el tamanio se calcula en base a los atributos + 3, por ejemplo 
                Int tiene 1 atributo (el valor) por lo que su tamanio es 3+1
                String tiene 2 atributos (el tamanio y el valor (el 0 al final)) por lo que su tamanio es 3+2
        - dispTab
        - atributos
"""
    # Ejemplo: nombre=Object, tag->0, tamanio=3, atributos=no tiene
    o.accum += """
    .word   -1 
Object_protObj:
    .word   0 
    .word   3 
    .word   Object_dispTab 
"""
    # Ejemplo: nombre=String, tag->4, tamanio=5, atributos=int ptr, 0
    o.accum += """
    .word   -1 
String_protObj:
    .word   4 
    .word   5 
    .word   String_dispTab 
    .word   int_const0 
    .word   0 
"""

def heap(o):
    o.accum += asm.heapStr

def global_text(o):
    o.accum += asm.textStr

def class_inits(o):
    pass


def genCode():
    o = Output()
    global_data(o)
    constants(o)
    # tables(o)
    # templates(o)
    # heap(o)
    # global_text(o)

    # TODO: Aquí enviar a un archivo, etc.
    print(o.out())
    
if __name__ == '__main__':
    # Ejecutar como: "python codegen.py <filename>" donde filename es el nombre de alguna de las pruebas
    #parser = CoolParser(CommonTokenStream(CoolLexer(FileStream("../resources/codegen/input/%s.cool" % sys.argv[1]))))
    parser = CoolParser(CommonTokenStream(CoolLexer(FileStream("./resources/codegen/input/%s.cool" % ("fact")))))
    walker = ParseTreeWalker()
    tree = parser.program()

    # Poner aquí los listeners necesarios para recorrer el árbol y obtener los datos
    # que requiere el generador de código
    setBaseClasses()
    walker.walk(DataListener(), tree)
    # for klass in _allClasses:
        # print(_allClasses[klass].name, _allClasses[klass].inherits)
    
    #walker.walk(Listener2(), tree)

    # Pasar parámetros al generador de código 
    genCode()