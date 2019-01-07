from entity.model import TreeNode
from lexer import *
from util.exception import ParseException, except_process

tokens_index = 0
exception_bofore = None

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
        node = TreeNode(token_name)
        node.line = tokens[tokens_index].pos[0]
        node.child=None
        tokens_index+=1
        return node
    else:
        raise ParseException('line %d index %d: unpected token,should be %s'
                             %(tokens[tokens_index].pos[0],tokens[tokens_index].pos[1],token_name))


def clear_exception():
    global exception_bofore
    if exception_bofore is not None:
        exception_bofore = None


def parse_stmt():
    """
    解析各种语句以及语句块
    """
    token = get_next_token()
    try:
        result = None
        if token.name=='if':
            result = parse_if_stmt()
        elif token.name=='while':
            result = parse_while_stmt()
        elif token.name=='in':
            result = parse_in_stmt()
        elif token.name=='out':
            result = parse_out_stmt()
        elif token.name in ['int','float','string']:
            result = parse_decl_stmt()
        elif token.name=='{':
            result = parse_block()
        elif token.type=='ID':
            result = parse_assign_stmt()
        if result is not None:
            clear_exception()
            return result
        else:
            skip_next_token()
            raise ParseException("line %d: position %d unpected token %s started"%(token.pos[0],token.pos[1],token.name))
    except ParseException as e:
        #当有异常出现时，判断是否语句的第一个异常，是则记录，并且该语句的后续错误均跳过，直到下一个可正确识别的句子为止
        global exception_bofore
        if exception_bofore is None:
            exception_bofore = e
            skip_exception(ParseException,e)
        if token.name in [';', '}']: clear_exception()


def parse_if_stmt():
    '''
    解析if语句
    '''
    node = TreeNode('IFSTMT')
    node.line = tokens[tokens_index].pos[0]
    check_next_token('if')
    check_next_token('(')
    node.add_child(parse_condition())
    check_next_token(')')
    temp = parse_stmt()
    if temp:node.add_child(temp)
    if get_next_token().name=='else':
        check_next_token('else')
        temp = parse_stmt()
        if temp: node.add_child(temp)
    return node if temp is not None else None


def parse_while_stmt():
    '''
    解析while语句
    '''
    node = TreeNode('WHILESTMT')
    node.line = tokens[tokens_index].pos[0]
    check_next_token('while')
    check_next_token('(')
    node.add_child(parse_condition())
    check_next_token(')')
    temp = parse_stmt()
    if temp: node.add_child(temp)
    return node if temp is not None else None


def parse_in_stmt():
    '''
    解析输入语句
    '''
    new_node = TreeNode('INSTMT')
    new_node.line = tokens[tokens_index].pos[0]
    check_next_token('in')
    check_next_token('(')
    new_node.add_child(parse_var())
    check_next_token(')')
    check_next_token(';')
    return new_node


def parse_out_stmt():
    '''
    解析输出语句
    '''
    new_node = TreeNode('OUTSTMT')
    new_node.line = tokens[tokens_index].pos[0]
    check_next_token('out')
    check_next_token('(')

    token = get_next_token()
    if token.type=='STR':
        new_node.add_child(parse_str())
    else:
        new_node.add_child(parse_expr())
    check_next_token(')')
    check_next_token(';')
    return new_node


def parse_decl_stmt():
    '''
    解析声明语句
    '''
    type_token = get_next_token()
    decl_node = TreeNode('VARDECL')
    type_node = TreeNode('TYPE')
    decl_node.line = tokens[tokens_index].pos[0]
    type_node.line = tokens[tokens_index].pos[0]
    decl_node.add_child(type_node)
    type_node.add_child(check_next_token(type_token.name))
    next_token = get_next_token()
    if next_token.name=='[':#判断声明是否为数组
        check_next_token('[')
        num_token = get_next_token()
        if num_token.type!='NUM' or '.' in num_token.name:#声明数组长度时需为正整数
            raise ParseException('Line %d: length of array should be a positive constant number'%num_token.pos[0])
        num_node = TreeNode('NUM')
        num_node.line = tokens[tokens_index].pos[0]
        num_node.value = num_token.name
        type_node.add_child(num_node)
        skip_next_token()
        check_next_token(']')
    id = parse_id()
    decl_node.add_child(id)
    next_name = get_next_token().name
    assfunc = parse_str if type_token.name=='string' else parse_expr
    while next_name in [',','=']:
        if next_name=='=':
            check_next_token('=')
            id.add_child(assfunc())
        else:
            check_next_token(',')
            id = parse_id()
            decl_node.add_child(id)
        next_name = get_next_token().name
    check_next_token(';')
    return decl_node


def parse_block():
    '''
    解析语句块
    '''
    new_node = TreeNode('BLOCK')
    new_node.line = tokens[tokens_index].pos[0]
    leftbrace = get_next_token()
    check_next_token('{')
    while get_next_token().name!='END' and get_next_token().name!='}':
        stmt = parse_stmt()
        if stmt:new_node.add_child(stmt)
    if get_next_token().name=='END':
        raise ParseException("Not matched closed } for { at line %d" %leftbrace.pos[0])
    check_next_token('}')
    return new_node


def parse_assign_stmt():
    '''
    解析赋值语句
    '''
    node = TreeNode('ASSIGNSTMT')
    node.line = tokens[tokens_index].pos[0]
    node.add_child(parse_var())
    check_next_token('=')
    token = get_next_token()
    if token.type=='STR':
        node.add_child(parse_str())
    else:
        node.add_child(parse_expr())
    check_next_token(';')
    return node


def parse_expr():
    '''
    解析表达式
    '''
    node = TreeNode('EXPR')
    node.line = tokens[tokens_index].pos[0]
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
    node.line = tokens[tokens_index].pos[0]
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
    node.line = tokens[tokens_index].pos[0]
    token = get_next_token()
    if token.type=='NUM':
        rnode = TreeNode('NUM')
        rnode.line = tokens[tokens_index].pos[0]
        rnode.value = token.name
        node.add_child(rnode)
        skip_next_token()
    elif token.name=='(':
        check_next_token('(')
        node.add_child(parse_expr())
        check_next_token(')')
    else:
        node.add_child(parse_var())
    return node


def parse_condition():
    '''
    解析整个条件布尔值
    '''
    condition_node = TreeNode('CONDITION')
    condition_node.line = tokens[tokens_index].pos[0]
    if get_next_token().name=='!':
        condition_node.add_child(check_next_token('!'))
        check_next_token('(')
        condition_node.add_child(parse_condition())
        check_next_token(')')
    else:
        condition_node.add_child(parse_cond())
        while get_next_token().name in ['&&','||']:
            condition_node.add_child(check_next_token(get_next_token().name))
            condition_node.add_child(parse_cond())
    return condition_node



def parse_compare():
    '''
    解析比较运算符
    '''
    token = get_next_token()
    if token.name in ['<','<=','==','<>']:
        node = check_next_token(token.name)
        node.line = tokens[tokens_index].pos[0]
        return node
    else:
        raise ParseException('Line %d: token should be a compare operand'%token.pos[0])


def parse_cond():
    '''
    解析单个条件布尔项
    '''
    cond_node = TreeNode('COND')
    cond_node.line = tokens[tokens_index].pos[0]
    if get_next_token().name=='!':
        cond_node.add_child(check_next_token('!'))
        check_next_token('(')
        cond_node.add_child(parse_cond())
        check_next_token(')')
    else:
        cond_node.add_child(parse_expr())
        cond_node.add_child(parse_compare())
        cond_node.add_child(parse_expr())
    return cond_node


def parse_var():
    '''
    解析变量，包括标识符及数组元素
    '''
    token = get_next_token()
    node = TreeNode('VAR')
    node.line = tokens[tokens_index].pos[0]
    if token.type=='ID':
        node.add_child(parse_id())
        next_token = get_next_token()
        if next_token.name=='[':
            check_next_token('[')
            node.add_child(parse_expr())
            check_next_token(']')
        return node
    else:
        raise ParseException('line %d: token should be a identifier'%token.pos[0])


def parse_id():
    '''
    解析标识符
    '''
    id_token = get_next_token()
    if id_token.type != 'ID':
        raise ParseException('Line %d: token should be a identifier' % id_token.pos[0])
    skip_next_token()
    rnode = TreeNode('ID')
    rnode.line = tokens[tokens_index].pos[0]
    rnode.value = id_token.name
    return rnode


def parse_str():
    '''
    解析字符串
    '''
    if get_next_token().type=='STR':
        rnode = TreeNode('STR')
        rnode.line = tokens[tokens_index].pos[0]
        rnode.value = get_next_token().name
        skip_next_token()
        return rnode
    else:
        raise ParseException('Line %d: token should be a string '%get_next_token().pos[0])


def parse(filename):
    '''
    语法分析主控程序，调用词法分析后，使用递归下降分析方法，不断进行语法分析，直至到tokens用完
    :param filename:
    :return:
    '''
    lexer(filename)
    tokens.append(Token('END','END',None))
    roots = TreeNode('root')
    while tokens_index < len(tokens)-1:
        result = parse_stmt()
        if result:roots.add_child(result)
    tokens.pop(-1)
    return roots


if __name__ == '__main__':
    filename = input('please input the cmm file name\n')
    roots=parse(filename)
    roots.print_tree()
    output_exception()
    input("press enter key to quit")
