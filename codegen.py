from antlr4 import *
from antlr.CoolLexer import *
from antlr.CoolParser import *
from antlr.CoolListener import *

import sys
import pathlib
import math
from string import Template
import asm
from data import DataListener
from structure import _allStrings, _allInts, _allClasses, _methodsAsm, _methodsOffsets
from structure import *
from text import TextListener

basicTags = dict(intTag=3, boolTag=4, stringTag=5)
filename = "fibo"

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
    classStart = _allStrings.index('Object') # TODO: Check if Object is always the first object
    
    # Class Name Table
    o.p('class_nameTab')
    for i in range(classStart, len(_allStrings)-1):
        o.p('.word', 'str_const{}'.format(i))

    # Class Object Table
    o.p('class_objTab')
    for klass in _allClasses:
        o.p('.word', '{}_protObj'.format(klass))
        o.p('.word', '{}_init'.format(klass)) 

    # Object Dispatch Table
    for klass in _allClasses.values():
        o.p('{}_dispTab'.format(klass.name))

        curr = klass.name
        methods = []
        currMethods = []

        # Obtener todos los metodos de esta clase
        for method in klass.methods:
            currMethods = ["{}.{}".format(curr, method)] + currMethods
        methods.extend(currMethods)
        
        # Obtener todos los metodos de las clases que hereda
        while curr != "Object":
            curr = _allClasses[curr].inherits
            currMethods = []
            for method in _allClasses[curr].methods:
                currMethods = ["{}.{}".format(curr, method)] + currMethods
            methods.extend(currMethods)
        
        offset = 0
        # Agregar métodos
        for i in range(len(methods)-1, -1, -1):
            o.p('.word', methods[i])
            _methodsOffsets["{}.{}".format(klass.name, methods[i].split(".")[1])] = offset
            offset += 1

def templates(o):
    i = 0
    for klass in _allClasses.values():
        o.p(".word", "-1")
        o.p("{}_protObj".format(klass.name))
        o.p(".word", i) # TODO: Check if tag is incremental
        
        size = 3 + len(klass.attributes) 
        o.p(".word", size)

        o.p(".word", "{}_dispTab".format(klass.name))

        if size>3:
            # TODO: Check how these values are generated
            for attrType in klass.attributes.values():
                if attrType == "String":
                    o.p(".word", "str_const{}".format(len(_allStrings)-1))
                elif attrType == "Int":
                    o.p(".word", "int_const0")
                else:
                    o.p(".word", "0")

        i += 1

def heap(o):
    o.accum += asm.heapStr

def global_text(o):
    o.accum += asm.textStr

def class_inits(o):
    for klass in _allClasses.values():
        o.p("{}_init".format(klass.name))
        o.accum += """    addiu	$sp $sp -12 
    sw	$fp 12($sp) 
    sw	$s0 8($sp) 
    sw	$ra 4($sp) 
    addiu	$fp $sp 4 
    move	$s0 $a0
"""
        if klass.inherits != klass.name:
            o.accum +='    jal {}_init\n'.format(klass.inherits)
        
        o.accum += """    move	$a0 $s0 
    lw	$fp 12($sp) 
    lw	$s0 8($sp) 
    lw	$ra 4($sp) 
    addiu	$sp $sp 12 
    jr	$ra 
"""

def genCode(walker, tree):
    o = Output()
    global_data(o)
    constants(o)
    tables(o)
    templates(o)
    heap(o)
    global_text(o)
    class_inits(o)
    
    walker.walk(TextListener(), tree)
    for methodAsm in _methodsAsm:
        o.accum += methodAsm

    # TODO: Aquí enviar a un archivo, etc.
    # print(o.out())
    folder_path = "./resources/codegen/output"
    
    pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True) 

    text_file = open(folder_path + "/%s.cl.s" % (filename), "w")
    text_file.write(o.out())
    text_file.close()
    
if __name__ == '__main__':
    # Ejecutar como: "python codegen.py <filename>" donde filename es el nombre de alguna de las pruebas
    #parser = CoolParser(CommonTokenStream(CoolLexer(FileStream("../resources/codegen/input/%s.cool" % sys.argv[1]))))
    parser = CoolParser(CommonTokenStream(CoolLexer(FileStream("./resources/codegen/input/%s.cool" % (filename)))))
    walker = ParseTreeWalker()
    tree = parser.program()

    # Poner aquí los listeners necesarios para recorrer el árbol y obtener los datos
    # que requiere el generador de código
    setBaseClasses()
    walker.walk(DataListener(), tree)

    # Pasar parámetros al generador de código 
    genCode(walker, tree)