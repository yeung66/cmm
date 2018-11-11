from lexer import *
from functools import wraps

tokens_index = 0


class ParseException(Exception):
    def __init__(self,mes):
        Exception.__init__(self,mes)


class TreeNode:
    indent = 0
    def __init__(self,type):
        self.type = type
        self.child = []
        self.value = None
        self.indent = 0

    def add_child(self,node):
        if self.child is not None:
            self.child.append(node)

    def print_tree(self):
        self.indent = TreeNode.indent
        prefix = '    ' * TreeNode.indent + '|---'
        if self.type=='root':
            prefix =''
        value = self.value if self.value else self.type
        print(prefix,value)
        if self.child is not None:
            TreeNode.indent+=1
            for c in self.child:
                c.print_tree()
            TreeNode.indent-=1


def except_process(func):
    '''
    函数装饰器，用于处理分析过程中出现异常，将其打印，并结束程序
    '''
    @wraps(func)
    def f(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except ParseException as e:
            print(e)
            exit(-1)
    return f


def get_next_token():
    '''
    返回当前token
    '''
    if tokens_index<len(tokens):
        return tokens[tokens_index]
    else:
        raise ParseException('lack of token at the end of code')


def skip_next_token():
    '''
    跳到下一个token
    '''
    global tokens_index
    tokens_index+=1


def check_next_token(token_name):
    '''
    检查当前token是否指定类型token，是则返回相应树节点，否则报错
    '''
    global tokens_index
    if tokens_index>=len(tokens):
        raise ParseException('lack of token %s at the end of code'%token_name)
    if tokens[tokens_index].name==token_name:
        tokens_index+=1
        node = TreeNode(token_name)
        node.child=None
        return node
    else:
        raise ParseException('line %d: unpected token,should be %s'%(tokens[tokens_index].pos[0],token_name))

@except_process
def parse_stmt():
    """
    解析各种语句以及语句块
    """
    token = get_next_token()
    if token.name=='if':
        return parse_if_stmt()
    elif token.name=='while':
        return parse_while_stmt()
    elif token.name=='in':
        return parse_in_stmt()
    elif token.name=='out':
        return parse_out_stmt()
    elif token.name in ['int','float','string']:
        return parse_decl_stmt()
    elif token.name=='{':
        return parse_block()
    elif token.type=='ID':
        return parse_assign_stmt()
    else:
        raise ParseException("line %d: position %d unpected token started"%token.pos)


def parse_if_stmt():
    '''
    解析if语句
    '''
    node = TreeNode('IFSTMT')
    node.add_child(check_next_token('if'))
    node.add_child(check_next_token('('))
    node.add_child(parse_condition())
    node.add_child(check_next_token(')'))
    node.add_child(parse_stmt())
    if get_next_token().name=='else':
        node.add_child('else')
        node.add_child(parse_stmt())
    return node


@except_process
def parse_while_stmt():
    '''
    解析while语句
    '''
    node = TreeNode('WHILESTMT')
    node.add_child(check_next_token('while'))
    node.add_child(check_next_token('('))
    node.add_child(parse_condition())
    node.add_child(check_next_token(')'))
    node.add_child(parse_stmt())
    return node


@except_process
def parse_in_stmt():
    '''
    解析输入语句
    '''
    new_node = TreeNode('INSTMT')
    new_node.add_child(check_next_token('in'))
    new_node.add_child(check_next_token('('))
    new_node.add_child(parse_var())
    new_node.add_child(check_next_token(')'))
    new_node.add_child(check_next_token(';'))
    return new_node


@except_process
def parse_out_stmt():
    '''
    解析输出语句
    '''
    new_node = TreeNode('OUTSTMT')
    new_node.add_child(check_next_token('out'))
    new_node.add_child(check_next_token('('))

    token = get_next_token()
    if token.type=='STR':
        new_node.add_child(parse_str())
    else:
        new_node.add_child(parse_expr())
    new_node.add_child(check_next_token(')'))
    new_node.add_child(check_next_token(';'))
    return new_node


@except_process
def parse_decl_stmt():
    '''
    解析声明语句
    '''
    type_token = get_next_token()
    decl_node = TreeNode('VARDECL')
    type_node = TreeNode('TYPE')
    decl_node.add_child(type_node)
    type_node.add_child(check_next_token(type_token.name))
    next_token = get_next_token()
    if next_token.name=='[':#判断声明是否为数组
        type_node.add_child(check_next_token('['))
        num_token = get_next_token()
        if num_token.type!='NUM' or '.' in num_token.name:#声明数组长度时需为正整数
            raise ParseException('Line %d: length of array should be a constant number'%num_token.pos[0])
        num_node = TreeNode('NUM')
        num_node.value = num_token.name
        type_node.add_child(num_node)
        skip_next_token()
        type_node.add_child(check_next_token(']'))
    id = parse_id()
    decl_node.add_child(id)
    next_name = get_next_token().name
    assfunc = parse_str if type_token.type=='STR' else parse_expr
    while next_name in [',','=']:
        if next_name=='=':
            id.add_child(check_next_token('='))
            id.add_child(assfunc())
        else:
            decl_node.add_child(check_next_token(','))
            id = parse_id()
            decl_node.add_child(id)
        next_name = get_next_token().name
    decl_node.add_child(check_next_token(';'))
    return decl_node


@except_process
def parse_block():
    '''
    解析语句块
    '''
    new_node = TreeNode('BLOCK')
    new_node.add_child(check_next_token('{'))
    while get_next_token().name!='}':
        new_node.add_child(parse_stmt())
    new_node.add_child(check_next_token('}'))
    return new_node


@except_process
def parse_assign_stmt():
    '''
    解析赋值语句
    '''
    node = TreeNode('ASSIGNSTMT')
    node.add_child(parse_var())
    node.add_child(check_next_token('='))
    token = get_next_token()
    if token.type=='STR':
        node.add_child(parse_str())
    else:
        node.add_child(parse_expr())
    node.add_child(check_next_token(';'))
    return node


def parse_expr():
    '''
    解析表达式
    '''
    node = TreeNode('EXPR')
    if get_next_token().name=='-':
        node.add_child(check_next_token('-'))
        node.add_child(parse_expr())
    else:
        node.add_child(parse_term())
        while get_next_token().name in ['+','-']:
            node.add_child(check_next_token(get_next_token().name))
            node.add_child(parse_term())
    return node

def parse_term():
    '''
    解析表达式中单个项
    '''
    node = TreeNode('TERM')
    node.add_child(parse_factor())
    while get_next_token().name in ['*', '/']:
        node.add_child(check_next_token(get_next_token().name))
        node.add_child(parse_factor())
    return node

def parse_factor():
    '''
    解析项中单个因子
    '''
    node = TreeNode('FACTOR')
    token = get_next_token()
    if token.type=='NUM':
        rnode = TreeNode('NUM')
        rnode.value = token.name
        node.add_child(rnode)
        skip_next_token()
    elif token.name=='(':
        node.add_child(check_next_token('('))
        node.add_child(parse_expr())
        node.add_child(check_next_token(')'))
    else:
        node.add_child(parse_var())
    return node


def parse_condition():
    '''
    解析整个条件布尔值
    '''
    condition_node = TreeNode('CONDITION')
    if get_next_token().name=='!':
        condition_node.add_child(check_next_token('!'))
        condition_node.add_child(check_next_token('('))
        condition_node.add_child(parse_condition())
        condition_node.add_child(check_next_token(')'))
    else:
        condition_node.add_child(parse_cond())
        while get_next_token().name in ['&&','||']:
            condition_node.add_child(check_next_token(get_next_token().name))
            condition_node.add_child(parse_cond())
    return condition_node


# def parse_other_condition():
#     other_condition = TreeNode('OTHERCONDITION')
#     other_condition.add_child(check_next_token(get_next_token().name))
#     other_condition.add_child(parse_cond())
#     if get_next_token().name in ['&&', '||']:
#         other_condition.add_child(parse_other_condition())
#     return other_condition



@except_process
def parse_compare():
    '''
    解析比较运算符
    '''
    token = get_next_token()
    if token.name in ['<','<=','==','<>']:
        return check_next_token(token.name)
    else:
        raise ParseException('Line %d: token should be a compare operand'%token.pos[0])


def parse_cond():
    '''
    解析单个条件布尔项
    '''
    cond_node = TreeNode('COND')
    if get_next_token().name=='!':
        cond_node.add_child(check_next_token('!'))
        cond_node.add_child(check_next_token('('))
        cond_node.add_child(parse_cond())
        cond_node.add_child(check_next_token(')'))
    else:
        cond_node.add_child(parse_expr())
        cond_node.add_child(parse_compare())
        cond_node.add_child(parse_expr())
    return cond_node


@except_process
def parse_var():
    '''
    解析变量，包括标识符及数组元素
    '''
    token = get_next_token()
    node = TreeNode('VAR')
    if token.type=='ID':
        node.add_child(parse_id())
        next_token = get_next_token()
        if next_token.name=='[':
            node.add_child(check_next_token('['))
            node.add_child(parse_expr())
            node.add_child(check_next_token(']'))
        return node
    else:
        raise ParseException('line %d: token should be a identifier'%token.pos[0])

@except_process
def parse_id():
    '''
    解析标识符
    '''
    id_token = get_next_token()
    if id_token.type != 'ID':
        raise ParseException('Line %d: token should be a identifier' % id_token.pos[0])
    skip_next_token()
    rnode = TreeNode('ID')
    rnode.value = id_token.name
    return rnode


def parse_str():
    '''
    解析字符串
    '''
    if get_next_token().type=='STR':
        rnode = TreeNode('STR')
        rnode.value = get_next_token().name
        skip_next_token()
        return rnode
    else:
        raise ParseException('Line %d: token should be a string '%get_next_token().pos[0])


def parser(filename):
    '''
    语法分析主控程序，调用词法分析后，使用递归下降分析方法，不断进行语法分析，直至到tokens用完
    :param filename:
    :return:
    '''
    lexer(filename)
    tokens.append(Token('END','END',None))
    roots = TreeNode('root')
    while tokens_index < len(tokens)-1:
        roots.add_child(parse_stmt())
    tokens.pop(-1)
    return roots


if __name__ == '__main__':
    filename = input('please input the cmm file name\n')
    roots=parser(filename)
    roots.print_tree()
    input("press enter key to quit")
