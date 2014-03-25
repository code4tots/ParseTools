from __future__ import print_function

from parse import (
    Stream, 
    Parser, 
    RegexParser,
    ParseFailed
)

whitespace = RegexParser(r'\s+')

Token = lambda regex : -whitespace + RegexParser(regex)

env = dict()

integer = Token(r'\d+') <= int
name    = Token(r'\w+')
var     = name          <= (lambda x : env[x])
opar    = Token(r'\(')
cpar    = Token(r'\)')
plus    = Token(r'\+')
dash    = Token(r'\-')
star    = Token(r'\*')
dstar   = Token(r'\*\*')
slash   = Token(r'\/')
eq      = Token(r'\=')
pr      = Token(r'print')
sc      = Token(r';')
end     = Token(r'$')

expr    = Parser(None)

prim    = ( integer
          | var
          | opar + expr - cpar
          )

expo         = Parser(None)
expo.parser  = ( (prim & dstar + expo <= (lambda a, b : a ** b))
                 | prim
                 )

unary        = Parser(None)
unary.parser = ( (plus + unary <= (lambda a : +a))
               | (dash + unary <= (lambda a : -a))
               | expo
               )

fact         = Parser(None)
fact.parser  = unary << ( (star  + unary,  (lambda a, b : a * b))
                        , (slash + unary,  (lambda a, b : a / b))
                        )

sum_         = Parser(None)
sum_.parser  = fact << ( (plus + fact, (lambda a, b : a + b))
                       , (dash + fact, (lambda a, b : a - b))
                       )

assign        = Parser(None)
assign.parser = ( (name - eq & assign <= (lambda name, value: (env.__setitem__(name,value),value)[-1]))
                | sum_
                )

print_        = Parser(None)
print_.parser = ( (pr + expr <= (lambda value: (print(value),value)[-1]))
                | assign
                )

expr.parser = print_

exprs        = Parser(None)
exprs.parser = ( expr + exprs
               | end
               )

try:
    p = exprs.parse(Stream('''
    print 1
    print 2
    x = 2 ** 3 * (2 + 45) - 5
    print 12
    print x + 2
    print x
    '''))

except ParseFailed as e:
    print(e.index)
    print(e.stream.stream[e.index])
    print(e.callstack)
    raise


