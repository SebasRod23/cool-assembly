from string import Template


gdStr1 = """
    .data
    .align  2
    .globl  class_nameTab
    .globl  Main_protObj
    .globl  Int_protObj
    .globl  String_protObj
    .globl  bool_const0
    .globl  bool_const1
    .globl  _int_tag
    .globl  _bool_tag
    .globl  _string_tag
"""

gdTpl1 = Template("""
_int_tag:
    .word   $intTag
_bool_tag:
    .word   $boolTag
_string_tag:
    .word   $stringTag
""")

gdStr2 = """
    .globl  _MemMgr_INITIALIZER
_MemMgr_INITIALIZER:
    .word   _NoGC_Init
    .globl  _MemMgr_COLLECTOR
_MemMgr_COLLECTOR:
    .word   _NoGC_Collect
    .globl  _MemMgr_TEST
_MemMgr_TEST:
    .word   0
"""

cTplInt = Template("""
    .word   -1
int_const$idx:
    .word   $tag
    .word   4
    .word   Int_dispTab
    .word   $value
""")

cTplStr = Template("""
    .word   -1
str_const$idx:
    .word   $tag
    .word   $size
    .word   String_dispTab
    .word   int_const$sizeIdx
    .ascii  "$value"
    .byte   0
    .align  2
""")

boolStr = Template("""
    .word   -1
bool_const0:
    .word   $tag
    .word   4
    .word   Bool_dispTab
    .word   0
    .word   -1
bool_const1:
    .word   $tag
    .word   4
    .word   Bool_dispTab
    .word   1
""")

heapStr = """
   .globl  heap_start 
heap_start:
    .word   0 
"""

textStr = """
    .text    
    .globl  Main_init 
    .globl  Int_init 
    .globl  String_init 
    .globl  Bool_init 
    .globl  Main.main 
"""

