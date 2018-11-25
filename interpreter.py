from re import match
from code_generator import generate, is_num
from util.SymbolTable import get_symbol_in_table, insert_symbol, init_symbol_table,symbol_table
from entity.model import Symbol
from util.exception import RunningError,except_process

cur_code = 0
level_count = 0 #记录代码/变量所在层次


def get_id(varname):
    """判断变量是否为数组元素，是则返回符号名和下标，否则返回符号名和False"""
    if '[' in varname:
        return varname[:varname.index('[')], varname[varname.index('[') + 1:-1]
    else:
        return varname, False


def get_var_value(varname):
    """传入一个变量名a或带下标的变量a[i]，返回该变量对应的符号和其值"""
    id, isarr = get_id(varname)
    symbol = get_symbol_in_table(id)
    value = symbol.arr[is_index_valid(symbol, isarr)] if isarr else symbol.value
    return symbol, value


def get_value(var):
    """对于四元式中的变量元素，若是数值则返回数值，变量则返回其值"""
    if var is None: return None
    if is_num(var):
        return eval(var)
    else:
        _, value = get_var_value(var)
        return value


def is_index_valid(symbol,index):
    """检查四元式中数组的下标是否合法，合法则返回实际的下标值"""
    if match(r'\d+',index):
        value = eval(index)
        if value < len(symbol.arr):#判断数组是否越界
            return value
        else: raise RunningError('Line %d: index %d out of bound in variable %s'%(symbol.declare_line,value,symbol.name))
    else:
        index_symbol = get_symbol_in_table(index)
        if index_symbol.type in ['NUM','int','float','temp']:
            if int(index_symbol.value)!=index_symbol.value:#判断下标是否为整数
                raise RunningError('Line %d: index %d of variable %s is float point number' % (symbol.declare_line,index_symbol.value, symbol.name))
            if -1 < index_symbol.value < len(symbol.arr):#判断数组是否越界
                return int(index_symbol.value)
            else:
                raise RunningError('Line %d: index %d out of bound in variable %s'%(symbol.declare_line,index_symbol.value,symbol.name))
        else:
            raise RunningError('Line %d: variable %s\'s index should be a non-negetive integer'%(symbol.declare_line,symbol.name))


@except_process(RunningError)
def interpret_fourcode(code):
    global cur_code,level_count
    type = code[0]
    if type == 'JMP':
        if code[1] is None or not get_symbol_in_table(code[1]).value:
            cur_code = code[3]
            return
    elif type == 'IN': level_count+=1
    elif type == 'OUT': level_count-=1
    elif type == 'READ': interpret_fourcode_read(code)
    elif type == 'WRITE': interpret_fourcode_write(code)
    elif type == 'ASSIGN': interpret_fourcode_assign(code)
    elif type in ['int','float','string']: interpret_fourcode_declare(code)
    else: interpret_fourcode_op(code)

    cur_code +=1


def interpret_fourcode_read(code):
    id, isarr = get_id(code[3])
    symbol = get_symbol_in_table(id)
    symbol.declare_line = code.line
    i = input()
    if i.startswith('"') and i.startswith('"'):  # 输入为字符串
        if symbol.type != 'string':
            raise RunningError('Line %d: should input a number to a number variable %s' % (code.line, symbol.name))
        if isarr:
            index = is_index_valid(symbol, isarr)
            symbol.arr[index] = i
        else:
            symbol.value = i
    elif is_num(i):
        if symbol.type == 'string':
            raise RunningError('Line %d: should input a string to a string variable %s' % (code.line, symbol.name))
        value = eval(i) * 1.0 if symbol.type == 'float' else int(eval(i))
        if isarr:
            index = is_index_valid(symbol, isarr)
            symbol.arr[index] = value
        else:
            symbol.value = value
    else:
        raise RunningError('Line %d: input is invalid'%code.line)


def interpret_fourcode_write(code):
    if code[2]: #输出一个变量的值
        _ , value = get_var_value(code[3])
        print(value[1:-1] if '"' in value else value)
    else:
        if '"' in code[3]:
            print(code[3][1:-1])
        else:print(code[3])


def interpret_fourcode_assign(code):
    to_id,to_isarr = get_id(code[1])
    to_symbol = get_symbol_in_table(to_id)
    if code[2]:#赋值内容为变量的值
        from_symbol, value = get_var_value(code[3])
    else:#直接将四元式第四项的内容赋给变量
        value = code[3]
    if to_isarr:
        to_symbol.declare_line = code.line
        to_index = is_index_valid(to_symbol,to_isarr)
        to_symbol.arr[to_index] = value
    else:
        to_symbol.value = value


def interpret_fourcode_declare(code):
    declare_type = code[0]
    symbol = Symbol(code[1],declare_type,level_count)
    init_value = 0 if declare_type == 'int' else 0.0 if declare_type == 'float' else ''
    if code[2]:#声明变量为数组
        #数组自动初始化变量
        symbol.arr = [init_value for i in range(int(code[2]))]
    else:
        if code[3]:#有初始化
            init_value = get_value(code[3])
        symbol.value = init_value
    symbol.declare_line = code.line
    insert_symbol(symbol)


def interpret_fourcode_op(code):
    op = code[0]
    v1, v2 = get_value(code[1]), get_value(code[2])
    value = None
    if op == '!':
        value = not v1 #逻辑取反
    elif op == '-':
        if v2 is None: value = - v1 #取负数
        else: value = eval(str(v1)+'-'+str(v2))
    elif op == '/':
        if v2==0: raise RunningError('Line %d: divisor cannot be zero!'%code.line)
        value = v1 / v2
    elif op == '&&':
        if not v1 : value = False # 考虑短路运算
        else: value = v2
    elif op == '||':
        if v1: value =True
        else: value = v2
    elif op == '<>':
        value = v1 != v2
    else:
        value = eval(str(v1)+op+str(v2))
    symbol = get_symbol_in_table(code[3])
    symbol.value = value


def run():
    filename = input('please input the cmm file name\n')
    codes = generate(filename)
    print('中间代码生成：')
    for i,c in enumerate(codes):
        print('%3d:'%i,c)
    print('------------------------------------------')
    print('\n代码执行结果：')
    print('------------------------------------------')
    init_symbol_table()
    while cur_code<len(codes):
        interpret_fourcode(codes[cur_code])



if __name__ == '__main__':
    run()