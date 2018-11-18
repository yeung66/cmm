from parse import tokens_index,parse_stmt
from lexer import *


filename = input('please input the cmm file name')
lexer(filename)
roots = []
while tokens_index<len(tokens):
    roots.append(parse_stmt())

print(roots)