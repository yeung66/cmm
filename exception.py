from functools import wraps
from sys import exit

class ParseException(Exception):
    def __init__(self,mes):
        Exception.__init__(self,mes)


class LexerException(Exception):
    def __init__(self,mes):
        Exception.__init__(self,mes)


class SemanticException(Exception):
    def __init__(self,mes):
        Exception.__init__(self,mes)


def except_process(t):
    '''
    函数装饰器，用于处理分析过程中出现异常，将其打印，并结束程序
    '''

    def f1(func):
        @wraps(func)
        def f(*args,**kwargs):
            try:
                return func(*args,**kwargs)
            except t as e:
                s = {ParseException:'ParseException',LexerException:'LexerException',SemanticException:'SemanticException'}
                print(s[t],'in',e)
                exit(-1)
        return f
    return f1