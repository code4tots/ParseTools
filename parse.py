class ParseException(Exception):
    def __init__(self,stream):
        self.stream = stream

    def __str__(self):
        return self.__class__.__name__ + '\n' + ''.join(
            '%s at %s (%s,%s)\n' % (
                parser,
                index,
                self.stream.lineno_at(index),
                self.stream.colno_at(index))
            for parser,index in self.stream.trace if parser.name is not None
        )

class ParseFailed(ParseException): pass
class FatalParseErr(ParseException): pass

class StringStream(object):
    def __init__(self,string,index=0):
        self.string = string
        self.index = index
        self.trace = []

    def line_around(self,index):
        b = self.string.rfind('\n',0,index)
        if b == -1: b = 0
        e = self.string.find('\n',index)
        if e == -1: e = len(self.string)
        return self.string[b:e]

    def lineno_at(self,index):
        return self.string.count('\n',0,index)

    def colno_at(self,index):
        b = self.string.rfind('\n',0,index)
        if b == -1: b = 0
        return index - b

class Parser(object):
    name = None
    def __init__(self,parser=None,name=None):
        self.parser = parser
        if name is not None: self.name = name
    
    def __call__(self,stream):
        stream.trace.append((self,stream.index))
        ret = self.parser(stream)
        stream.trace.pop()
        return ret
    
    def __add__(self,other):
        a = self.parsers  if isinstance(self ,ChainParser) else (self,)
        b = other.parsers if isinstance(other,ChainParser) else (other,)
        return ChainParser(a+b)
    
    def __or__(self,other):
        a = self .parsers if isinstance(self ,TryParser) else (self,)
        b = other.parsers if isinstance(other,TryParser) else (other,)
        return TryParser(a+b)
    
    def __mul__(self,n):
        return ExactlyNTimesParser(self,n)
    
    def __pow__(self,n):
        return AtLeastNTimesParser(self,n)
    
    def __truediv__(self,n):
        return AtMostNTimesParser(self,n)
    
    def __mod__(self,action):
        return ActionParser(self,action)
    
    def __pos__(self):
        return FatalParser(self)

    def __str__(self):
        return self.name
    
class RegexParser(Parser):
    def __init__(self,regex):
        import re
        self.regex = re.compile(regex)
    
    def __call__(self,stream):
        m = self.regex.match(stream.string,stream.index)
        
        if m is None:
            raise ParseFailed(stream)
        
        stream.index = m.end()
        
        return m.group()

class ChainParser(Parser):
    def __init__(self,parsers):
        self.parsers = parsers
    
    def __call__(self,stream):
        result = []
        for p in self.parsers:
            m = p(stream)
            if m is not None:
                result.append(m)
        return result

class TryParser(Parser):
    def __init__(self,parsers):
        self.parsers = parsers
    
    def __call__(self,stream):
        save = stream.index
        for parser in self.parsers:
            try:                return parser(stream)
            except ParseFailed: stream.index = save
        raise ParseFailed(stream)

class ExactlyNTimesParser(Parser):
    def __init__(self,parser,n):
        self.parser = parser
        self.n = n

    def __call__(self,stream):
        result = []
        for _ in range(self.n):
            m = self.parser(stream)
            if m is not None:
                result.append(m)
        return result

class AtLeastNTimesParser(Parser):
    def __init__(self,parser,n):
        self.parser = parser
        self.n = n
    
    def __call__(self,stream):
        result = []
        begin = stream.index
        try:
            while True:
                save = stream.index
                m = self.parser(stream)
                if m is not None:
                    result.append(m)
        except ParseFailed:
            stream.index = save
        
        if len(result) < self.n:
            stream.index = begin
            raise ParseFailed(stream)
        
        return result

class AtMostNTimesParser(Parser):
    def __init__(self,parser,n):
        self.parser = parser
        self.n = n
    
    def __call__(self,stream):
        result = []
        try:
            for _ in range(self.n):
                save = stream.index
                m = self.parser(stream)
                if m is not None:
                    result.append(m)
        except ParseFailed:
            stream.index = save
        return result

class ActionParser(Parser):
    def __init__(self,parser,action):
        self.parser = parser
        self.action = action
    
    def __call__(self,stream):
        return self.action(self.parser(stream))

class FatalParser(Parser):
    def __init__(self,parser):
        self.parser = parser
    
    def __call__(self,stream):
        try:                self.parser(stream)
        except ParseFailed: raise FatalParseErr(stream)

class ReturnNoneParser(Parser):
    def __init__(self,parser):
        self.parser = parser
    
    def __call__(self,stream):
        self.parser(stream)

class SeparatorParser(Parser):
    def __init__(self,parser,separator):
        self.parser = parser
        self.separator = separator
    
    def __call__(self,stream):
        try:                self.separator(stream)
        except ParseFailed: pass
        return self.parser(stream)
