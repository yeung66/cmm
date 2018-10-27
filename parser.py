from lexer import *

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

    def add_child(self,node):
        if self.child is not None:
            self.child.append(node)

    def print_tree(self):
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
    def f(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except ParseException as e:
            print(e)
            exit(-1)
    return f

def get_next_token():
    if tokens_index<len(tokens):
        return tokens[tokens_index]
    else:
        raise ParseException('lack of token at the end of code')


def skip_next_token():
    global tokens_index
    tokens_index+=1

def check_next_token(token_name):
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
    :return:
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
        raise ParseException("line %d: position %d unpected token"%token.pos)

@except_process
def parse_if_stmt():
    node = TreeNode('IFSTMT')
    node.add_child(check_next_token('if'))
    node.add_child(check_next_token('('))
    node.add_child(check_next_token(parse_condition()))
    node.add_child(check_next_token(')'))
    node.add_child(parse_stmt())
    if get_next_token().name=='else':
        node.add_child('else')
        node.add_child(parse_stmt())
    return node


@except_process
def parse_while_stmt():
    node = TreeNode('WHILESTMT')
    node.add_child(check_next_token('('))
    node.add_child(check_next_token(parse_condition()))
    node.add_child(check_next_token(')'))
    node.add_child(parse_stmt())


@except_process
def parse_in_stmt():
    new_node = TreeNode('INSTMT')
    new_node.add_child(check_next_token('in'))
    new_node.add_child(check_next_token('('))
    new_node.add_child(parse_var())
    new_node.add_child(check_next_token(')'))
    new_node.add_child(check_next_token(';'))
    return new_node


@except_process
def parse_out_stmt():
    new_node = TreeNode('OUTSTMT')
    new_node.add_child(check_next_token('out'))
    new_node.add_child(check_next_token('('))

    token = get_next_token()
    if token.type=='ID':
        new_node.add_child(parse_var())
    elif token.type=='STR':
        new_node.add_child(check_next_token(token.name))
    else:
        new_node.add_child(parse_expr())
    new_node.add_child(check_next_token(')'))
    new_node.add_child(check_next_token(';'))
    return new_node

@except_process
def parse_decl_stmt():
    id_token = get_next_token()
    decl_node = TreeNode('VARDECL')
    type_node = TreeNode('TYPE')
    decl_node.add_child(type_node)
    type_node.add_child(check_next_token(id_token.name))
    next_token = get_next_token()
    if next_token.name=='[':
        type_node.add_child(check_next_token('['))
        num_token = get_next_token()
        if num_token.type!='NUM':
            raise ParseException('Line %d: length of array should be a constant number'%num_token.pos[0])
        type_node.add_child(check_next_token(num_token.name))
        type_node.add_child(check_next_token(']'))
    decl_node.add_child(parse_id())
    while get_next_token().name==',':
        decl_node.add_child(check_next_token(','))
        decl_node.add_child(parse_id())
    decl_node.add_child(check_next_token(';'))
    return decl_node


@except_process
def parse_block():
    new_node = TreeNode('BLOCK')
    new_node.add_child(check_next_token('{'))
    while get_next_token().name!='}':
        new_node.add_child(parse_stmt())
    new_node.add_child(check_next_token('}'))
    return new_node


@except_process
def parse_assign_stmt():
    node = TreeNode('ASSIGNSTMT')
    node.add_child(parse_var())
    node.add_child(check_next_token('='))
    token = get_next_token()
    if token.type=='STR':
        node.add_child(check_next_token(token.name))
    else:
        node.add_child(parse_expr())
    node.add_child(check_next_token(';'))
    return node


def parse_expr():
    pass


def parse_condition():
    condition_node = TreeNode('CONDITION')
    if get_next_token().name=='!':
        condition_node.add_child(check_next_token('!'))
        condition_node.add_child(parse_condition())
    else:
        condition_node.add_child(parse_cond())
        if get_next_token().name in ['&&','||']:
            condition_node.add_child(check_next_token(get_next_token().name))
            condition_node.add_child(parse_condition)
    return condition_node


@except_process
def parse_compare():
    token = get_next_token()
    if token.name in ['<','<=','==','<>']:
        return TreeNode(token.name)
    else:
        raise ParseException('Line %d: token should be a compare operand'%token.pos[0])


def parse_cond():
    cond_node = TreeNode('COND')
    cond_node.add_child(parse_expr())
    cond_node.add_child(parse_compare())
    cond_node.add_child(parse_expr())
    return cond_node


@except_process
def parse_var():
    token = get_next_token()
    node = TreeNode('VAR')
    if token.type=='ID':
        node.add_child(check_next_token(token.name))
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
    id_token = get_next_token()
    if id_token.type != 'ID':
        raise ParseException('Line %d: token should be a identifier' % id_token.pos[0])
    skip_next_token()
    return TreeNode(id_token.name)

@except_process
def parse_cond():
    pass

if __name__ == '__main__':
    filename = input('please input the cmm file name\n')
    lexer(filename)
    roots=TreeNode('root')
    while tokens_index < len(tokens):
        roots.add_child(parse_stmt())
    roots.print_tree()

