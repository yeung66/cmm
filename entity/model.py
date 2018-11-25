
class Token:
    def __init__(self,type,name,pos):
        self.type = type
        self.name = name
        self.pos = pos

    def output(self):
        print('(%d, %s, %s)'%(self.pos[0],self.name,self.type))

class TreeNode:
    indent = 0
    def __init__(self,type):
        self.type = type
        self.child = []
        self.value = None
        self.indent = 0
        self.line = 0

    def add_child(self,node):
        if self.child is not None:
            self.child.append(node)

    def get_child(self,i):
        if self.child:
            return self.child[i]

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

class FourCode:
    def __init__(self,first,second,third,fourth):
        self.__code = [first,second,third,fourth]
        self.line = None

    def __getitem__(self, item):
        if isinstance(item,int) and -1<item<4:
            return self.__code[item]

    def __setitem__(self, key, value):
        if isinstance(key,int) and -1<key<4:
            self.__code[key]=value

    def __str__(self):
        return '(%10s, %10s,%10s,%10s)'%self.get_code()

    def get_code(self):
        return tuple(self.__code)


class Symbol:
    def __init__(self,name,type,level):
        self.name = name
        self.type = type
        self.level = level
        self.next = None
        self.arr = None
        self.declare_line = None
        self.value = None

    def is_array(self):
        return self.arr is not None
