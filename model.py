
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

class FourCode:
    def __init__(self,first,second,third,fourth):
        self.__code = [first,second,third,fourth]

    def __getitem__(self, item):
        if isinstance(item,int) and 0<item<4:
            return self.__code[item]

    def __setitem__(self, key, value):
        if isinstance(key,int) and 0<key<4:
            self.__code[key]=value

    def get_code(self):
        return tuple(self.__code)
