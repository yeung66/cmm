from code_generator import generate,get_symbol_in_table,get_temp_symbol
from model import FourCode,Symbol


cur_code = 0
symbol_table = {'symbol_list':[],'temp_list':[]} #符号表
level_count = 0 #记录代码/变量所在层次


def interpret_fourcode(code):
    global cur_code
    type = code[0]
    if type == 'JMP':
        if code[0] is None or not get_symbol_in_table(code[1]).value:
            cur_code = code[3]

    cur_code +=1


def run():
    filename = input('please input the cmm file name\n')
    codes = generate(filename)
    while cur_code<len(codes):
        interpret_fourcode(codes[cur_code])