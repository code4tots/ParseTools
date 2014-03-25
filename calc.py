from __future__ import print_function
from parse import Stream, Parser, Regex

env = dict()

ws = Regex(r'\s*')

Tok = lambda regex : ws + Regex(regex)

end = Tok(r'$') <= (lambda _: None)
num = Tok(r'[\+\-]?(\d+\.?)|(\d*\.\d+)') <= float
nam = Tok(r'\w+')
var = nam <= (lambda x : env[x])
plus  = Tok(r'\+')
dash  = Tok(r'\-')
star  = Tok(r'\*')
slash = Tok(r'\/')
mod   = Tok(r'\%')
dstar = Tok(r'\*\*')
opar  = Tok(r'\(')
cpar  = Tok(r'\)')
equal = Tok(r'\=')
rr    = Tok(r'\>\>')

exprs = Parser()
expr = Parser()
prim = Parser()
expo = Parser()
sign = Parser()
fact = Parser()
summ = Parser()
asgn = Parser()
prin = Parser()

prim.parser = num | var | opar + expr - cpar
expo.parser = (
    (prim - dstar & expo <= (lambda a, b: a ** b)) |
    prim
)
sign.parser = (
    (plus + sign <= (lambda x : +x)) |
    (dash + sign <= (lambda x : -x)) |
    expo
)
fact.parser = sign << (
    (star  + sign, (lambda a, b : a * b)),
    (slash + sign, (lambda a, b : a / b)),
    (mod   + sign, (lambda a, b : a % b))
)
summ.parser = fact << (
    (plus + fact, (lambda a,b: a + b)),
    (dash + fact, (lambda a,b: a - b))
)
asgn.parser = (
    (nam - equal & asgn <= (lambda n,v : (env.__setitem__(n,v),v)[-1])) |
    summ
)

prin.parser = (
    (rr + expr <= (lambda x : (print(x),x)[-1])) |
    asgn
)

expr.parser = prin

exprs.parser = expr + exprs | expr

exprs('''
>> a = 4
b = 5
a + b
>> a + b
''')