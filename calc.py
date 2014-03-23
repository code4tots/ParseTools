from __future__ import print_function

from parse import (
    Stream, 
    Parser, 
    RegexParser as RP, 
    OptionalParser as Optional,
    ParseFailed
)

whitespace = RP(r'\s+')

Token = lambda regex : Optional(whitespace) + RP(regex)

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
end     = Token(r'$')

expr    = Parser(None)

prim    = ( integer
          | name
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

<<<<<<< HEAD
print_         = Parser(name='print')
print_.parser  = ( (prin & exp) % (lambda x : print(x[0]))
                 | assign
                 )
=======
print_        = Parser(None)
print_.parser = ( (pr + expr <= (lambda value: print(value)))
                | assign
                )
>>>>>>> cleanup

expr.parser = print_

exprs        = Parser(None)
exprs.parser = ( expr + exprs
               | end
               )

try:
<<<<<<< HEAD
    calc(StringStream('''
    1+2
=======
    p = exprs.parse(Stream('''
    print x = 2 ** 3 * (2 + 45) - 5
>>>>>>> cleanup
    '''))

except ParseFailed as e:
    print(e.index)
    print(e.stream.stream[e.index])
    print(e.callstack)
    raise
    
else:
    print(p)
    print(type(p))

