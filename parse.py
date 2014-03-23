class ParseException(Exception):
    def __init__(self,stream):
        self.callstack = list(stream.callstack)
        self.index = stream.index
        self.stream = stream

class ParseFatal(ParseException):
    pass

class CorruptCallStack(ParseFatal):
    pass

class ParseFailed(ParseException):
    pass

class LeftRecursion(ParseFailed):
    pass

class Stream(object):
    def __init__(self,stream,index=0):
        self.stream = stream
        self.index = index
        self.callstack = []
        self.callers = set()
        self.memo_value = dict()
        self.memo_index = dict()

class StreamContextManager(object):
    def __init__(self,parser,stream):
        self.parser = parser
        self.stream = stream
        self.index = stream.index
        self.context = id(parser) * len(stream.stream) + stream.index
    
    def __enter__(self):
        if self.context in self.stream.callers:
            raise LeftRecursion(self.stream)
        
        self.stream.callers.add(self)
        self.stream.callstack.append(self)
        
        return self.context
    
    def __exit__(self,type_,value,traceback):
        if len(self.stream.callstack) == 0 or self.stream.callstack.pop() is not self:
            raise CorruptCallStack(self.stream)
        
        self.stream.callers.remove(self)
        
        if isinstance(value,ParseFailed):
            self.stream.memo_value[self.context] = None
    
    def __repr__(self):
        return self.parser.__class__.__name__ + ' ' + str(self.index)
            
class Parser(object):
    def __init__(self,delegate_parser):
        self.parser = delegate_parser
    
    def _parse(self,stream):
        return self.parser.parse(stream)
    
    def parse(self,stream):
        with StreamContextManager(self,stream) as context:
            if context not in stream.memo_value:
                stream.memo_value[context] = self._parse(stream)
                stream.memo_index[context] = stream.index
            
            if stream.memo_value[context] is None:
                raise ParseFailed(stream)
            
            stream.index = stream.memo_index[context]
            return stream.memo_value[context]
    
    def __and__(self,other):
        a = self .parsers if isinstance(self ,ConcatenationParser) else [self ]
        b = other.parsers if isinstance(other,ConcatenationParser) else [other]
        return ConcatenationParser(a + b)
    
    def __or__(self,other):
        a = self .parsers if isinstance(self ,AlternationParser) else [self ]
        b = other.parsers if isinstance(other,AlternationParser) else [other]
        return AlternationParser(a + b)
    
    def __add__(self,other):
        return PrefixedParser(self,other)
    
    def __sub__(self,other):
        return SuffixedParser(self,other)
    
    def __le__(self,action):
        return ActionParser(self,action)
    
    def __lshift__(self,suffixes):
        return ReduceParser(self,suffixes)

class RegexParser(Parser):
    def __init__(self,regex):
        import re
        self.original_regex = regex
        self.regex = re.compile(regex)
    
    def _parse(self,stream):
        match = self.regex.match(stream.stream,stream.index)
        
        if match is not None:
            stream.index = match.end()
            return match.group()
    
    def __repr__(self):
        return 'RegexParser(\'%s\')'%self.original_regex

class ConcatenationParser(Parser):
    def __init__(self,parsers):
        self.parsers = parsers
    
    def _parse(self,stream):
        results = []
        for parser in self.parsers:
            result = parser.parse(stream)
            if result is not None:
                results.append(result)
        return results
    
    def __le__(self,action):
        return ActionParser(self, lambda xs : action(*xs))

class AlternationParser(Parser):
    def __init__(self,parsers):
        self.parsers = parsers
    
    def _parse(self,stream):
        match_begin = stream.index
        for parser in self.parsers:
            try:                return parser.parse(stream)
            except ParseFailed: stream.index = match_begin
        raise ParseFailed(stream)

class PrefixedParser(Parser):
    def __init__(self,prefix,body):
        self.prefix = prefix
        self.body = body
    
    def _parse(self,stream):
        self.prefix.parse(stream)
        return self.body.parse(stream)

class SuffixedParser(Parser):
    def __init__(self,body,suffix):
        self.body = body
        self.suffix = suffix
    
    def _parse(self,stream):
        body = self.body.parse(stream)
        self.suffix.parse(stream)
        return body

class ActionParser(Parser):
    def __init__(self,parser,action):
        self.parser = parser
        self.action = action
    
    def _parse(self,stream):
        return self.action(self.parser.parse(stream))

class ReduceParser(Parser):
    def __init__(self,base,suffixes):
        self.base = base
        self.suffixes = suffixes
    
    def _parse(self,stream):
        result = self.base.parse(stream)
        while True:
            next_match_start = stream.index
            
            for parser, action in self.suffixes:
                try:
                    result = action(result,parser.parse(stream))
                    break
                except ParseFailed:
                    next_match_start = stream.index
                    
            if next_match_start == stream.index:
                break
        
        return result
        
class OptionalParser(Parser):
    def __init__(self,parser):
        self.parser = parser
    
    def _parse(self,stream):
        try:
            return self.parser.parse(stream)
        except ParseFailed:
            return False
