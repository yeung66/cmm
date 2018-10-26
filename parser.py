from lexer import *

tokens_index = 0

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


def get_next_token():
    if tokens_index<len(tokens):
        return tokens[tokens_index]

def check_next_token(token_name):
    global tokens_index
    if tokens[tokens_index].name==token_name:
        tokens_index+=1
        node = TreeNode(token_name)
        node.child=None
        return node
    else:
        raise Exception('line %d: position %d unpected token'%tokens[tokens_index].pos)

def parse_stmt():
    try:
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
            print("line %d: position %d unpected token"%token.pos)
            exit(-1)
    except Exception as e:
        print(e)


def parse_if_stmt():
    pass

def parse_while_stmt():
    pass

def parse_in_stmt():
    try:
        new_node = TreeNode('INSTMT')
        new_node.add_child(check_next_token('in'))
        new_node.add_child(check_next_token('('))
        new_node.add_child(parse_id())
        new_node.add_child(check_next_token(')'))
        new_node.add_child(check_next_token(';'))
        return new_node
    except Exception as e:
        print(e)

def parse_out_stmt():
    try:
        new_node = TreeNode('OUTSTMT')
        new_node.add_child(check_next_token('out'))
        new_node.add_child(check_next_token('('))

        token = get_next_token()
        if token.type=='ID':
            new_node.add_child(parse_id())
        elif token.type=='STR':
            new_node.add_child(check_next_token(token.name))
        else:
            new_node.add_child(parse_expr())

        new_node.add_child(check_next_token(')'))
        new_node.add_child(check_next_token(';'))
        return new_node
    except Exception as e:
        print(e)


def parse_decl_stmt():
    pass

def parse_block():
    new_node = TreeNode('BLOCK')
    try:
        new_node.add_child(check_next_token('{'))
        while get_next_token().name!='}':
            new_node.add_child(parse_stmt())
        new_node.add_child(check_next_token('}'))
        return new_node
    except Exception as e:
        print(e)

def parse_assign_stmt():
    pass

def parse_id():
    pass

def parse_expr():
    pass

if __name__ == '__main__':
    filename = input('please input the cmm file name\n')
    lexer(filename)
    roots=TreeNode('root')
    while tokens_index < len(tokens):
        roots.add_child(parse_stmt())
    roots.print_tree()

