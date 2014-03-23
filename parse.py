class ParseException(Exception):
    pass

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
        self.memo = dict()

class StreamContextManager(object):
    def __init__(self,parser,stream):
        self.parser = parser
        self.stream = stream
        self.index = stream.index
        self.context = id(stream.parser) * len(stream.stream) + stream.index
    
    def __enter__(self):
        if self in self.stream.callstack:
            raise LeftRecursion(self.stream)
        
        self.stream.callstack.append(self)
        
        return self.context
    
    def __exit__(self,type_,value,traceback):
        if len(self.stream.callstack) == 0 or self.stream.callstack.pop() is not self:
            raise CorruptCallStack(stream)
        
        if isinstance(value,ParseFailed):
            self.stream.memo[self.context] = None
            
class Parser(object):
    def __init__(self,delegate_parser):
        self._delegate_parser = delegate_parser
    
    def _parse(self,stream):
        return self._delegate_parser.parse(stream)
    
    def parse(self,stream):
        with StreamContextManager(self,stream) as context:
            if context not in stream.memo:
                stream.memo[context] = self._parse(stream)
            
            if stream.memo[context] is None:
                raise ParseFailed(stream)
            
            else:
                return stream.memo[context]

class RegexParser(Parser):
    def __init__(self,regex):
        import re
        self.regex = re.compile(regex)
    
    def _parse(self,stream):
        match = self.regex.match(stream.stream,stream.index)
        
        if match is None:
            raise ParseFailed(stream)
        
        stream.index = match.end()
        return match.group()

class SingletonParser(Parser):
    def __init__(self,parse_function):
        self.parse_function = parse_function
    
    def _parser(self,stream):
        return self.parse_function(stream)
