from parse import Parser, RegexParser as RP, empty_parser as empty

space = RP(r'\s*')
token = lambda r : space & RP(r)
equal = token(r'\=')
name  = token(r'\w+')
slit  = token(r'\"((\\\")|[^\"])*\"')
vline = token(r'\|')
aand  = token(r'\&')
opar  = token(r'\(')
cpar  = token(r'\)')
obra  = token(r'\[')
cbra  = token(r'\]')
end   = token(r'$')

expr         = Parser()

exprs        = Parser()
exprs.parser = expr & exprs | empty

pexpr        = slit | name | (opar & expr & cpar & empty)

fex          = Parser()
fex.parser   = obra & exprs & cbra & empty & fex | empty
fexpr        = pexpr & fex | pexpr

aex          = Parser()
aex.parser   = aand & fexpr & aex | empty
aexpr        = fexpr & aex | fexpr

vex          = Parser()
vex.parser   = vline & aexpr & vex | empty
vexpr        = aexpr & vex | aexpr

expr.parser  = vexpr

line         = name & equal & expr

lines        = Parser()
lines.parser = line & lines | end

p = lines.parse('''
f = token[a]
''')
print(p)



