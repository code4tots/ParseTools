'''
AST code
'''




'''
Parsing code
'''


from parse import (
    Stream,
    Parser,
    RegexParser,
    ParseException
)

whitespace = RegexParser(r'\s+')

Token = lambda regex : -whitespace + RegexParser(regex)

floating    = Token(r'[\+\-]?(\.\d*)|(\d+\.\d*)') <= float
integer     = Token(r'[\+\-]?\d+')                <= int
identifier  = Token(r'\w+')
open_paren  = Token(r'\(')
close_paren = Token(r'\)')
kw_function = Token(r'function')

function_def = 

print(floating.parse(Stream('''

function 

''')))

