from os.path import exists,isfile
from sys import exit

KEYWORD = ['if','else','while','int','float','string','in','out']
OPERATOR = ['+','-','*','/','=','<','<=','==','<>','&','|','^','&&','||','!']
BLOCK = ['[',']','(',')','{','}',';','"',',','.']
tokens = []

class Token:
    def __init__(self,type,name,pos):
        self.type = type
        self.name = name
        self.pos = pos

    def output(self):
        print('(%d, %s, %s)'%(self.pos[0],self.name,self.type))

def remove_comment(resource):
    """
    删除注释及无用字符（保留换行符以后续记录行号
    :param resource: str
    :return str
    """
    code_without_comment = []
    pos = 0
    rowlines = 1
    startline = rowlines
    try:
        while pos<len(resource):
            if resource[pos]=='/' and resource[pos+1]=='/':
                while resource[pos]!='\n':
                    pos+=1
            elif resource[pos]=='/' and resource[pos+1]=='*':
                pos+=2
                startline = rowlines
                while resource[pos]!='*' or resource[pos+1]!='/':
                    if resource[pos]=='\n':#移除注释仍保留原始行位置
                        rowlines+=1
                        code_without_comment.append('\n')
                    pos+=1
                pos+=2
            if pos==len(resource):break#防止多行注释在最后一行造成越界
            if resource[pos] not in ['\t','\v','\r']:
                code_without_comment.append(resource[pos])
                rowlines = rowlines+1 if resource[pos]=='\n' else rowlines
            pos+=1
    except Exception:
        #多行注释未正确结束
        print('line %d: comment not end rightly'%startline)
        exit(-1)
    return ''.join(code_without_comment)

def isLetter(char):
    return 'a'<=char<='z' or 'A'<=char<='Z'

def scan(row,line):
    """
    核心函数，输入单行字符串以识别token，并将其添加至全局变量处
    :param row: 单行字符串
    :param line:  行号
    :return:
    """
    row = row.strip()
    n = len(row)
    row = row + '#'#在末尾添加以特殊符号以防后探过程中数组访问越界
    index = 0

    while index<n:
        # try:
        start = index
        if row[index]==' ':#读入空白字符则跳过
            index+=1
            continue
        if isLetter(row[index]):#识别标识符
            if index!=0 and str.isdigit(row[index-1]) or row[index]=='_':
                #判断标识符是否合法
                print('illegal identifier in line %d'%line)
                exit(-1)
            index+=1
            while isLetter(row[index]) or str.isdigit(row[index]) or row[index]=='_':
                index+=1
            token_str = row[start:index]
            if token_str in KEYWORD:
                tokens.append(Token('KEYWORD',token_str,(line,index)))
            else:
                if token_str[-1]=='_':
                    print('illegal identifier in line %d'%line)
                    exit(-1)
                tokens.append(Token('ID',token_str,(line,index)))
        elif str.isdigit(row[index]):
            while str.isdigit(row[index]):
                index+=1
            tokens.append(Token('NUM', row[start:index], (line, index)))
        elif row[index] == '"':#处理字符串
            index+=1
            while index<len(row) and row[index]!='"':
                index+=1
            if index==len(row):
                print('string not end rightly in line %d! '%line)
                exit(-1)
            else:
                index+=1
                tokens.append(Token('STR',row[start:index],(line,index)))
        elif row[index] == '=': # =,==
            if row[index+1]=='=':
                tokens.append(Token('OPERATOR', '==', (line, index)))
                index+=2
            else:
                tokens.append(Token('OPERATOR', '=', (line, index)))
                index+=1
        elif row[index]=='<':# <. <=, <>
            if row[index+1]=='=':
                tokens.append(Token('OPERATOR', '<=', (line, index)))
                index+=2
            elif row[index+1]=='>':
                tokens.append(Token('OPERATOR', '<>', (line, index)))
                index+=2
            else:
                tokens.append(Token('OPERATOR', '<', (line, index)))
                index+=1
        elif row[index]=='|':
            if row[index+1]=='|':
                tokens.append(Token('OPERATOR', '||', (line, index)))
                index+=1
            else:
                tokens.append(Token('OPERATOR', '|', (line, index)))
            index+=1
        elif row[index]=='&':
            if row[index+1]=='&':
                tokens.append(Token('OPERATOR', '&&', (line, index)))
                index+=1
            else:
                tokens.append(Token('OPERATOR', '&', (line, index)))
            index+=1
        elif row[index] in OPERATOR or row[index] in BLOCK:
            type = 'OPERATOR' if row[index] in OPERATOR else 'BLOCK'
            tokens.append(Token(type,row[index],(line,index)))
            index+=1
        else:
            print('unknown word appear in line %d, index %d'%(line,index))
            exit(-1)

def lexer(filename):
    """
    词法分析主控程序，将token存于全局变量tokens中
    :param filename:
    :return:
    """
    if not (exists(filename) and isfile(filename)):
        print('file dose not exist!')
        exit(-1)
    with open(filename,'r',encoding='UTF-8') as f:
        process_code = remove_comment(f.read())
        line = 0
        for row in process_code.split('\n'):
            line+=1
            scan(row,line)
    return tokens


if __name__ == '__main__':
    filename = input('please input the cmm file path!\n')
    lexer(filename)
    for t in tokens:
        t.output()
    input('\npress enter key to quit')