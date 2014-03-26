from parse import ParseException, ActionFailed, Stream, Parser, Regex

keywords = frozenset([
    'template'
])

'''
AST and code generation
'''

class AST(object):
    'superclass of all code generators'

class Word(AST):
    def __init__(self,string):
        if string in keywords:
            raise ActionFailed()
        self.string = string

class Typename(AST):
    ''

class TypeIdentifier(Typename,Word):
    def __init__(self,string):
        self.string = string

class Expression(AST):
    ''

class Int(Expression):
    def __init__(self,string):
        self.int_ = int(string)
        self.string = string

class Float(Expression):
    def __init__(self,string):
        self.float_ = float(string)
        self.string = string

class StringLiteral(Expression):
    def __init__(self,string):
        self.string = string

class CharacterLiteral(Expression):
    def __init__(self,string):
        self.string = string

class Identifier(Expression,Word):
    pass

class Binop(Expression):
    pass

class Unop(Expression):
    pass

class Addition(Binop):
    pass

class Subtraction(Binop):
    pass


'''
construct parser
'''

ws = Regex(r'\s*')

Token = lambda regex : ws + Regex(regex)

float_            = Token(r'[\+\-]?(\d+\.)|(\d*\.\d+)') < Float
int_              = Token(r'[\+\-]?\d+')                < Int
stringliteral     = Token(r'\"((\\\")|[^\"])*\"')       < StringLiteral
characterliteral  = Token(r"\'((\\\')|[^\'])*\'")       < CharacterLiteral
word              = Token(r'\w+')
identifier        = word                                < Identifier
typeidentifier    = word                                < TypeIdentifier
semicolon         = Token(r'\;')
comma             = Token(r'\,')
open_parenthesis  = Token(r'\(')
close_parenthesis = Token(r'\)')
open_bracket      = Token(r'\[')
close_bracket     = Token(r'\]')
open_brace        = Token(r'\{')
close_brace       = Token(r'\}')
kw_template       = Token(r'template')



