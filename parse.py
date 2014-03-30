class Stream(object):
    def __init__(self,string):
        self.string = string
        self.index = 0
        self.memo = dict()
    
    @property
    def state(self):
        return self.index
    
    @state.setter
    def state(self,new_state):
        self.index = new_state

class ParseFailed(Exception):
    pass

parse_failed = object()
class BaseParser(object):
    def parse(self,stream):
        if isinstance(stream,str):
            stream = Stream(stream)
        
        old_state = stream.state
        
        if (self,old_state) not in stream.memo:
            try:
                return_value = self._parse(stream)
                new_state = stream.state
                stream.memo[self,old_state] = return_value, new_state
        
            except ParseFailed:
                stream.state = old_state
                stream.memo[self,old_state] = None, parse_failed
        return_value, new_state = stream.memo[self,old_state]
        
        if new_state is parse_failed:
            raise ParseFailed(stream)
        
        stream.state = new_state
        return return_value
    
    def __and__(self,other):
        return AndParser(self,other)
    
    def __or__(self,other):
        return OrParser(self,other)

class Parser(BaseParser):
    def __init__(self,parser=None):
        self.parser = parser
    
    def _parse(self,stream):
        return self.parser.parse(stream)

class RegexParser(BaseParser):
    def __init__(self,regex):
        import re
        self.regex = re.compile(regex)
    
    def _parse(self,stream):
        m = self.regex.match(stream.string,stream.index)
        if m is None:
            raise ParseFailed(stream)
        stream.index = m.end()
        return m.group()

class AndParser(BaseParser):
    def __init__(self,a,b):
        self.a = a
        self.b = b
    
    def _parse(self,stream):
        return (self.a.parse(stream),self.b.parse(stream))

class OrParser(BaseParser):
    def __init__(self,a,b):
        self.a = a
        self.b = b
    
    def _parse(self,stream):
        try:
            return self.a.parse(stream)
        except ParseFailed:
            pass
        
        return self.b.parse(stream)

class EmptyParser(BaseParser):
    'singleton'
    def _parse(self,stream):
        pass
    
empty_parser = EmptyParser()