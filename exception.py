class ParseException(Exception):
    def __init__(self,mes):
        Exception.__init__(self,mes)