class ParseFailed(Exception): pass
class FatalParseErr(Exception): pass

class StringStream(object):
    def __init__(self,string,index=0):
        self.string = string
        self.index = index

class Parser(object):
    '''
    By default, Parser class delegates the parsing to another parser,
    self.parser
    
    For more sophisticated state based behavior, you may wish to
    subclass Parser and override __call__ and __init__ (as is done by the
    utility subclasses of Parser below)
    
    Note that the parser function doesn't have to be set at time of creation.
    
    This could be used as a forward declaration mechanism.
    '''
    def __init__(self,parser=None):
        self.parser = parser
    
    def __call__(self,stream):
        return self.parser(stream)
    
    def __add__(self,other):
        '''
        Concatenate two parsers
        '''
        a = self.parsers  if isinstance(self ,ChainParser) else (self,)
        b = other.parsers if isinstance(other,ChainParser) else (other,)
        return ChainParser(a+b)
    
    def __or__(self,other):
        '''
        Alternate one or other
        '''
        a = self .parsers if isinstance(self ,TryParser) else (self,)
        b = other.parsers if isinstance(other,TryParser) else (other,)
        return TryParser(a+b)
    
    def __mul__(self,n):
        '''
        Repeat self exactly n times
        '''
        a = self.parsers if isinstance(self,ChainParser) else (self,)
        return ChainParser(a * n)
    
    def __pow__(self,n):
        '''
        Repeat self at least n times
        '''
        return AtLeastNTimesParser(self,n)
    
    def __truediv__(self,n):
        '''
        Repeat self at most n times
        '''
        return AtMostNTimesParser(self,n)
    
    def __div__(self,n):
        return self.__truediv__(n)
    
    def __mod__(self,action):
        '''
        Apply an action -- modify return value of parser
        '''
        return ActionParser(self,action)
    
    def __pos__(self):
        '''
        Marks parser as critical
        This means if ParseFailed is raised,
        it is caught and instead a FatalParseErr is thrown.
        '''
        return FatalParser(self)
    
    def __invert__(self):
        '''
        ~self
        Returns None on match.
        
        Decided against using this as ReturnNoneParser,
        as ~self kind of looks like "don't match self"
        
        Instead import ReturnNoneParser as Drop for a more
        conevenient way to use it
        '''
        # return ReturnNoneParser(self)
    
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

class FlattenParser(Parser):
    def __init__(self,parser):
        self.parser = parser
    
    def __call__(self,stream):
        result = []
        for xs in self.parser(stream):
            result.extend(xs)
        return result

