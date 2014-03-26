from parse import Parser, Regex, ActionFailed

class AST(object):
    pass

class Int(AST):
    def __init__(self,string):
        self.string = string

class Float(AST):
    def __init__(self,string):
        self.string = string

class Name(AST):
    def __init__(self,string):
        self.string = string

class FunctionCall(object):
    def __init__(self,f,args):
        self.f = f
        self.args = args

end   = Regex(r'$')
space = Regex(r'\s*')
empty = space

Token = lambda r : space + Regex(r)

float_ = Token(r'[\+\-]?(\d+\.)|(\d*\.\d+)') < Float
int_   = Token(r'[\+\-]?\d+')                < Int
name   = Token(r'\w+')                       < Name


