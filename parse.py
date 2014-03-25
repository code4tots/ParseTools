class ParseException(Exception):
    'base exception'
    def __init__(self,stream=None):
        self.set_stream(stream)
    
    def set_stream(self,stream):
        self.stream = stream
        self.index = stream.index
        self.callstack = list(stream.callstack)

class ParseFatal(ParseException):
    'unrecoverable -- should be caught by user'

class LeftRecursion(ParseFatal):
    'left recursion indicates something wrong with grammar'

class ParseFailed(ParseException):
    'thrown around a lot when pattern does not match'

class ActionFailed(ParseFailed):
    'when user action indicates parse should fail'

class Stream(object):
    'Should be subclassed for extra behavior (e.g. indent stack)'
    def __init__(self,string):
        self.string = string
        self.index = 0
        self.callstack = []
        self.callers = set()
        self.memo_value = dict()
        self.memo_index = dict()

fail_indicator = object()

class Parser(object):
    'subclasses should override __init__ and _parse'
    def __init__(self,parser=None):
        self.parser = parser
    
    def _parse(self,stream):
        return self.parser(stream)
    
    def __call__(self,stream):
        if isinstance(stream,str):
            stream = Stream(stream)
        
        h = id(self) * len(stream.string) + stream.index
        
        if h in stream.callers:
            raise LeftRecursion(stream)
        
        if h not in stream.memo_value:
            stream.callstack.append((self,stream.index))
            stream.callers.add(h)
            
            try:
                stream.memo_value[h] = self._parse(stream)
                stream.memo_index[h] = stream.index
                
            except ParseFailed:
                stream.memo_value[h] = fail_indicator
                raise
                
            finally:
                stream.callstack.pop()
                stream.callers.remove(h)
        
        if stream.memo_value[h] is fail_indicator:
            raise ParseFailed(stream)
        
        stream.index = stream.memo_index[h]
        return stream.memo_value[h]
    
    def __and__(self,other):
        a = self .parsers if isinstance(self ,And) else [self ]
        b = other.parsers if isinstance(other,And) else [other]
        return And(a+b)
    
    def __or__(self,other):
        a = self .parsers if isinstance(self ,Or) else [self ]
        b = other.parsers if isinstance(other,Or) else [other]
        return Or(a+b)
    
    def __add__(self,other):
        return Second(self,other)
    
    def __sub__(self,other):
        return First(self,other)
    
    def __le__(self,action):
        return Action(self,action)
    
    def __lshift__(self,alternatives):
        return Reduce(self,alternatives)

class Regex(Parser):
    'essentially all terminals'
    def __init__(self,regex):
        import re
        self.regex = re.compile(regex)
    
    def _parse(self,stream):
        match = self.regex.match(stream.string,stream.index)
        if match is None:
            raise ParseFailed(stream)
        stream.index = match.end()
        return match.group()

class And(Parser):
    'Fixed number -- if count unknown, should prefer a chaining mechanism'
    def __init__(self,parsers):
        self.parsers = parsers
    
    def _parse(self,stream):
        return [parser(stream) for parser in self.parsers]
    
    def __le__(self,action):
        return Action(self,lambda xs : action(*xs))

class Or(Parser):
    'one of alternatives'
    def __init__(self,parsers):
        self.parsers = parsers
    
    def _parse(self,stream):
        index = stream.index
        for parser in self.parsers:
            try:                return parser(stream)
            except ParseFailed: stream.index = index
        raise ParseFailed(stream)

class First(Parser):
    'keeps just the result of first parser'
    def __init__(self,a,b):
        self.a = a
        self.b = b
    
    def _parse(self,stream):
        x = self.a(stream)
        self.b(stream)
        return x

class Second(Parser):
    'keeps just the result of the second parser'
    def __init__(self,a,b):
        self.a = a
        self.b = b
    
    def _parse(self,stream):
        self.a(stream)
        return self.b(stream)

class Action(Parser):
    'changes return value'
    def __init__(self,parser,action):
        self.parser = parser
        self.action = action
    
    def _parse(self,stream):
        return self.action(self.parser(stream))

class Reduce(Parser):
    'to aid in left recursive grammars'
    def __init__(self,parser,alternatives):
        self.parser = parser
        self.alternatives = alternatives
    
    def _parse(self,stream):
        x = self.parser(stream)
        while True:
            match_begin = stream.index
            
            for parser, action in self.alternatives:
                try:                x = action(x,parser(stream))
                except ParseFailed: stream.index = match_begin
                else:               break
                
            if match_begin == stream.index:
                break
        return x
