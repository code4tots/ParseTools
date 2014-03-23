'''
Simple calculator to test out my parse.py

I realize that the associativity of multiplicative and additive expressions
is wrong ... but it's kinda annoying to do it the other way ...

Hopefully soon I'll try to figure out some way to elegantly handle left 
recursion ...
'''

from __future__ import print_function

from parse import (
    Parser,
    StringStream,
    RegexParser,
    SeparatorParser,
    ReturnNoneParser as Drop,
    ParseException
)

space = RegexParser(r'\s+')
Token = lambda r : SeparatorParser(RegexParser(r),space)

variables = dict()

number = Token(r'\d+\.?\d+') % float
name   = Token(r'\w+')
var    = name                % (lambda x : variables[x] if x in variables else 0)
plus   = Token(r'\+')
minus  = Token(r'\-')
dstar  = Token(r'\*\*')
star   = Token(r'\*')
slash  = Token(r'\/')
opar   = Token(r'\(')
cpar   = Token(r'\)')
eq     = Token(r'\=')
prin   = Token(r'print')

exp    = Parser(name='expr')
par    = (Drop(opar) + exp + Drop(cpar)) % (lambda xs : xs[0])
prim   = par | number | var


power          = Parser()
power.parser   = ( (prim + Drop(dstar) + +power) % (lambda xs : xs[0] ** xs[1])
                 | prim
                 )

unary          = Parser(name='unary')
unary.parser   = ( (Drop(plus)  + +unary) % (lambda xs : +xs[0])
                 | (Drop(minus) + +unary) % (lambda xs : -xs[0])
                 | power
                 )

fact           = Parser(name='fact')
fact.parser    = ( (unary + Drop(star)  + +fact) % (lambda xs : xs[0] * xs[1])
                 | (unary + Drop(slash) + +fact) % (lambda xs : xs[0] / xs[1])
                 | unary
                 )

sum_           = Parser(name='sum')
sum_.parser    = ( (fact  + Drop(plus)  + +sum_) % (lambda xs : xs[0] + xs[1])
                 | (fact  + Drop(minus) + +sum_) % (lambda xs : xs[0] - xs[1])
                 | fact
                 )

assign         = Parser(name='assign')
assign.parser  = ( (name + Drop(eq) + exp) % (lambda xs : variables.__setitem__(xs[0],xs[1]) or xs[1])
                 | sum_
                 )

print_         = Parser(name='print')
print_.parser  = ( (prin & exp) % (lambda x : print(x[0]))
                 | assign
                 )

exp.parser = print_

calc = exp ** 1
try:
    calc(StringStream('''
    1+2
    '''))
except ParseException as e:
    print(e)

