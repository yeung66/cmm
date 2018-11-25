from entity.model import TreeNode, Symbol
from util.exception import SemanticException

symbol_table = {'symbol_list':[],'temp_list':[]} #符号表


def init_symbol_table():
    symbol_table['symbol_list'] = []
    symbol_table['temp_list'] = []


def get_symbol_in_table(node):
    id = node
    prefix = ''
    if isinstance(node,TreeNode):
        id = node.value
        prefix = 'line %d: '%node.line
    if not id.startswith('*'):
        for sym in symbol_table['symbol_list']:
            if sym.name ==id:
                return sym
    else:
        for sym in symbol_table['temp_list']:
            if sym.name ==id:
                return sym
        temp = Symbol(id,'temp',0)
        insert_symbol(temp,type='temp_list')
        return temp
    raise SemanticException('%s variable %s is not declared'%(prefix,id))


def get_temp_symbol(type):
    for i in range(1000):
        name = '*temp'+str(i)
        exist = False
        for s in symbol_table['temp_list']:
            if s.name==name:
                exist=True
        if not exist:
            symbol = Symbol(name,type,0)
            insert_symbol(symbol,'temp_list')
            return symbol.name


def insert_symbol(symbol,type='symbol_list'):

    for i,sym in enumerate(symbol_table[type]):
        if sym.name == symbol.name:
            if sym.level >= symbol.level:
                raise SemanticException('line %d: variable %s has been declared'%(symbol.declare_line,symbol.name))
            symbol.next = sym
            symbol_table[type][i] = symbol
            return
    symbol_table[type].append(symbol)


def clear_symbol_level(level):
    """退出层级代码块后清除该层声明的变量"""
    for i,s in enumerate(symbol_table['symbol_list']):
        if s.level == level:
            symbol_table['symbol_list'][i]=s.next
    symbol_table['symbol_list'] = list(filter(None,symbol_table['symbol_list']))


def clear_temp_symbol():
    symbol_table['temp_list'] = []