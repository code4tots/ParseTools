from parse import Stream, Parser, ActionFailed, Regex

class AST(object):
    pass

class Expression(AST):
    pass

class Int(Expression):
    def __init__(self,string):
        try:               self.int = int(string)
        except ValueError: raise ActionFailed()
    
    def eval(self,env):
        return self.int

class Float(Expression):
    def __init__(self,string):
        try:               self.float = float(string)
        except ValueError: raise ActionFailed()
    
    def eval(self,env):
        return self.float

class Name(Expression):
    def __init__(self,string):
        if string == 'print':
            raise ActionFailed()
        self.string = string
    
    def eval(self,env):
        return env[self.string]

class Binop(Expression):
    def __init__(self,a,b):
        self.a = a
        self.b = b

class Unop(Expression):
    def __init__(self,x):
        self.x = x

class Pow(Binop):
    def eval(self,env):
        return self.a.eval(env) ** self.b.eval(env)

class Mul(Binop):
    def eval(self,env):
        return self.a.eval(env) * self.b.eval(env)

class Div(Binop):
    def eval(self,env):
        return self.a.eval(env) / self.b.eval(env)

class Mod(Binop):
    def eval(self,env):
        return self.a.eval(env) % self.b.eval(env)

class Add(Binop):
    def eval(self,env):
        return self.a.eval(env) + self.b.eval(env)

class Sub(Binop):
    def eval(self,env):
        return self.a.eval(env) - self.b.eval(env)

class Pos(Unop):
    def eval(self,env):
        return +self.x.eval(env)

class Neg(Unop):
    def eval(self,env):
        return -self.x.eval(env)

class Asgn(Binop):
    def eval(self,env):
        env[self.a.string] = self.b.eval(env)
        return env[self.a.string]

class Prin(Unop):
    def eval(self,env):
        r = self.x.eval(env)
        print(r)
        return r

class Exprs(Unop):
    def eval(self,env):
        x = self.x
        while x is not None:
            r, x = x
            r.eval(env)

ws = Regex(r'\s*')
end = Regex(r'$')

Tok = lambda regex : ws + Regex(regex)

end   = Tok(r'$')                         < (lambda _: None)
flt   = Tok(r'[\+\-]?(\d+\.)|(\d*\.\d+)') < Float
int_  = Tok(r'[\+\-]?\d+')                < Int
nam   = Tok(r'\w+')                       < Name
var   = nam
plus  = Tok(r'\+')
dash  = Tok(r'\-')
star  = Tok(r'\*')
slash = Tok(r'\/')
mod   = Tok(r'\%')
dstar = Tok(r'\*\*')
opar  = Tok(r'\(')
cpar  = Tok(r'\)')
equal = Tok(r'\=')
kw_print = Tok(r'print')

exprs = Parser()
exprl = Parser()
expr  = Parser()
prim  = Parser()
expo  = Parser()
sign  = Parser()
fact  = Parser()
summ  = Parser()
asgn  = Parser()
prin  = Parser()

prim.parser = flt | int_ | var | opar + expr - cpar
expo.parser = (
    (prim - dstar & expo < Pow) |
    prim
)
sign.parser = (
    (plus + sign < Pos) |
    (dash + sign < Neg) |
    expo
)
fact.parser = sign << (
    (star  + sign, Mul),
    (slash + sign, Div),
    (mod   + sign, Mod)
)
summ.parser = fact << (
    (plus + fact, Add),
    (dash + fact, Sub)
)
asgn.parser = (
    (nam - equal & asgn < Asgn) |
    summ
)

prin.parser = (
    (kw_print + expr < Prin) |
    asgn
)

expr.parser = prin

exprl.parser = (
    (expr & exprl < (lambda a,b: (a,b))) | 
    (end          < (lambda x  : None ))
)

exprs.parser = exprl < Exprs

r = exprs('''
a = 4
b = 5
a + b
print(a + b ** (2+3))
print 3
print a ** b
''')
d = dict()
r.eval(d)

