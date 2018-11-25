from re import match
from entity.model import FourCode
from parse import parse
from util.SymbolTable import *
from util.exception import except_process

codes = [] #存放中间代码四元式
line_count = 0 #记录四元式行数
level_count = 0 #记录代码/变量所在层次


def add_code(fourcode):
    global line_count
    codes.append(fourcode)
    line_count+=1


def enter_level():
    global level_count
    add_code(FourCode('IN', None, None, None))
    level_count+=1


def quit_level():
    global level_count
    add_code(FourCode('OUT', None, None, None))
    clear_symbol_level(level_count)
    level_count-=1


def is_str_symbol_from_expr(value):
    #判断表达式解析得到的结果是否字符串（当表达式只有单个string变量时会出现
    if type(value) == str and not is_num(value):
        temp_sym = get_symbol_in_table(value) if '[' not in value else get_symbol_in_table(value[:value.index('[')])
        return temp_sym.type == 'string'
    return False


def is_num(string):
    """判断字符串是否为数字形式"""
    return match('-?\d+(.\d+)?',string)


@except_process(SemanticException)
def interpret(node):
    """
    解析每一个语句节点或块节点
    :param node:
    :return:
    """
    if node.type == 'IFSTMT':
        interpret_ifstmt(node)
    elif node.type == 'BLOCK':
        for child in node.child:
            interpret(child)
    elif node.type == 'WHILESTMT':
        interpret_whilestmt(node)
    elif node.type == 'INSTMT':
        interpret_readstmt(node)
    elif node.type == 'OUTSTMT':
        interpret_outstmt(node)
    elif node.type == 'VARDECL':
        interpret_declare(node)
    elif node.type == 'ASSIGNSTMT':
        interpret_assign(node)
    clear_temp_symbol()


def interpret_ifstmt(node):
    if node.type == 'IFSTMT':
        false_jmp = FourCode('JMP',interpret_condition(node.get_child(0)),None,None)
        add_code(false_jmp)
        enter_level()
        interpret(node.get_child(1))
        quit_level()
        if len(node.child)>2:
            out_jmp = FourCode('JMP',None,None,None)
            add_code(out_jmp)
            false_jmp[3]=line_count
            enter_level()
            interpret(node.get_child(2))
            quit_level()
            out_jmp[3] = line_count
        else:
            false_jmp[3] = line_count


def interpret_whilestmt(node):
    if node.type == 'WHILESTMT':
        init_line = line_count
        false_jmp = FourCode('JMP', interpret_condition(node.get_child(0)), None, None)
        add_code(false_jmp)
        enter_level()
        interpret(node.get_child(1))
        add_code(FourCode('JMP', None, None, init_line))
        quit_level()
        false_jmp[3] = line_count


def interpret_readstmt(node):
    if node.type == 'INSTMT':
        varnode = node.get_child(0)
        symbol = get_symbol_in_table(varnode.get_child(0))
        if len(varnode.child) == 2:#变量为数组成员
            if not symbol.is_array():
                raise SemanticException('line %d: variable %s is not an array'%(node.line,symbol.name))
            index = interpret_index(varnode)
            four_code = FourCode('READ',None,None,varnode.get_child(0).value+'[%s]'%str(index))
        else:
            four_code = FourCode('READ',None,None,varnode.get_child(0).value)
        four_code.line = node.line
        add_code(four_code)


def interpret_outstmt(node):
    if node.type == 'OUTSTMT':
        if node.get_child(0).type == 'STR':
            four_code = FourCode('WRITE',None,0,node.get_child(0).value)
        else:
            expr = interpret_expr(node.get_child(0))
            four_code = FourCode('WRITE', None, 1, expr)
            if is_num(expr): four_code[2] = 0
        four_code.line = node.line
        add_code(four_code)


def interpret_declare(node):
    type = node.get_child(0)
    if len(type.child)==2:#声明的变量为数组
        length = type.get_child(1).value
        for i in node.child[1:]:
            add_code(FourCode(type.get_child(0).type,i.value,length,None))
            symbol = Symbol(i.value,type.get_child(0).type,level_count)
            symbol.arr = []
            symbol.declare_line = node.line
            insert_symbol(symbol)
    else:
        for i in node.child[1:]:
            value = interpret_expr(i.get_child(0)) if i.child else None
            add_code(FourCode(type.get_child(0).type,i.value,None,value))
            symbol = Symbol(i.value, type.get_child(0).type, level_count)
            symbol.declare_line = node.line
            insert_symbol(symbol)


def interpret_assign(node):
    varnode = node.get_child(0)
    symbol = get_symbol_in_table(varnode.get_child(0))
    code = FourCode('ASSIGN',symbol.name,None,None)
    value_node = node.get_child(1)
    if value_node.type=='STR':
        if symbol.type!='string':#将数值赋给字符串
            raise SemanticException('Line %d: not match type in assignment statement' % node.line)
        code[2] = 0
        code[3] = value_node.value
    else:
        value = interpret_expr(value_node)
        if is_str_symbol_from_expr(value) and symbol.type!='string':#将字符串赋值给数值变量
            raise SemanticException('Line %d: not match type in assignment statement' % node.line)
        code[2] = 1 if not is_num(value) else 0
        code[3] = value

    if symbol.is_array() or len(varnode.child)==2:
        if symbol.is_array() and len(varnode.child)==2:
            index = interpret_index(varnode)
            code[1] = code[1]+'['+index+']'
        else:
            arr = '' if symbol.is_array() else 'not '
            raise SemanticException('Line %d: variable %s is %san array!'%(node.line,node.value,arr))

    add_code(code)


def interpret_index(node):
    index = interpret_expr(node.get_child(1))
    if is_str_symbol_from_expr(index):  # 用字符串变量作下标
        raise SemanticException('Line %d: cannot use a string variable as index' % node.line)
    if match(r'\d+.\d+',index):# 用浮点数变量作下标
        raise SemanticException('Line %d: cannot use a float point number as index' % node.line)
    return index


def interpret_condition(node):
    if node.get_child(0).type=='!':#取反
        result = get_temp_symbol('bool')
        code = FourCode('!',interpret_condition(node.get_child(1)),None,result)
        add_code(code)
        return result
    else:
        if len(node.child)==1:
            return interpret_cond(node.get_child(0))
        else:
            last_operand = interpret_cond(node.get_child(0))
            for i,cond in enumerate(node.child):
                if cond.type=='COND':continue
                else:
                    if cond.type=='&&':#实现短路运算
                        jmp = FourCode('JMP',last_operand,None,None)
                    else:
                        temp = get_temp_symbol('bool')
                        add_code(FourCode('!',last_operand,None,temp))
                        jmp = FourCode('JMP',temp,None,None)
                    add_code(jmp)
                    add_code(FourCode(cond.type,last_operand,interpret_cond(node.get_child(i+1)),last_operand))
                    jmp[3] = line_count
            return last_operand


def interpret_cond(node):
    result = get_temp_symbol('bool')
    if node.get_child(0).type=='!':#取反
        add_code(FourCode('!', interpret_cond(node.get_child(1)), None, result))
        return result
    else:
        add_code(FourCode(node.get_child(1).type,interpret_expr(node.get_child(0)),interpret_expr(node.get_child(2)),result))
        return result


def interpret_expr(node):
    if node.get_child(0).type == '-':  #取负数
        result = get_temp_symbol('num')
        add_code(FourCode('-',interpret_expr(node.get_child(1)),None,result))
        return result
    else:
        if len(node.child)==1:
            return interpret_term(node.get_child(0))
        else:
            last_operand = interpret_term(node.get_child(0))
            for i,op in enumerate(node.child):
                if op.type=='TERM':continue
                else:
                    temp_symbol = get_temp_symbol('NUM')
                    add_code(FourCode(op.type,last_operand,interpret_term(node.get_child(i+1)),temp_symbol))
                    last_operand = temp_symbol
            return last_operand


def interpret_term(node):
    if len(node.child)==1:
        return interpret_factor(node.get_child(0))
    else:
        last_operand = interpret_factor(node.get_child(0))
        if is_str_symbol_from_expr(last_operand):
            raise SemanticException('Line %d: string cannot in operation!'%node.line)
        for i, op in enumerate(node.child):
            if op.type == 'FACTOR':
                continue
            else:
                next_operand = interpret_factor(node.get_child(i + 1))
                if is_str_symbol_from_expr(next_operand):
                    raise SemanticException('Line %d: string cannot in operation!' % node.line)
                temp = get_temp_symbol('NUM')
                code = FourCode(op.type, last_operand, next_operand, temp)
                add_code(code)
                code.line = node.line
                last_operand = temp
        return last_operand


def interpret_factor(node):
    child = node.get_child(0)
    if child.type == 'NUM':
        return child.value
    elif child.type == 'VAR':
        symbol = get_symbol_in_table(child.get_child(0))
        if symbol.is_array() or len(child.child) == 2:
            if symbol.is_array() and len(child.child) == 2: #数组元素
                index = interpret_index(child)
                return symbol.name+'[%s]'%str(index)
            else:
                arr = '' if symbol.is_array() else 'not '
                raise SemanticException('Line %d: variable %s is %san array!' % (node.line, node.value, arr))
        return symbol.name
    else:
        return interpret_expr(child)


def generate(filename):
    init_symbol_table()
    roots = parse(filename)
    for c in roots.child:
        interpret(c)
    return codes

if __name__ == '__main__':
    filename = input('please input the cmm file name\n')
    for i,c in enumerate(generate(filename)):
        print('%3d: '%i,c)