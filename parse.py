'''
parse.py
========

My original goal in desigining parse.py was to make a memoized top down
parser that is flexible enough to handle all sorts of usecases easily.

However, I soon realized things that required state (like indent sensitive
parsing, parenthesis nested sensitive whitespace, typename parsing, etc.)
became quite a hassle to handle...

So I just made a Parser framework that just handled all of *my* usecases
out of the box. This of course makes the parser less epic and flexible...
but hopefully it will be useful for a lot of things...
'''

class ParseException(Exception):
    'base exception'

class FatalParse(ParseException):
    'encountered something so bad that we should end parsing'

class LeftRecursion(FatalParse):
    'thrown if there is a left recursion encountered in the grammar'

class MismatchedClosure(FatalParse):
    'extra close parenthesis/bracket/brace was encountered'

class ParseFailed(ParseException):
    'default exception thrown when unable to parse'

class Stream(object):
    '''
    Stream
    ======
    
    '''
    def __init__(self,string):
        'string to parse'
        self.string = string
        
        '''
        state variables
        index -> current index in string
        istack -> indentation stack
        depth -> parenthesis/bracket/brace depth
        '''
        self.index = 0
        self.istack = ('',None)
        self.depth = 0
        
        'for memoizing results and new states'
        self.memo = dict()
        
        '''
        call information
        cstack -> call stack
        callers -> stuff that are trying to parse this stream
        '''
        self.cstack = []
        self.callers = set()
    
    @property
    def state(self):
        return (self.index,self,istack,self.pdepth)
    
    @state.setter
    def state(self,new_state):
        self.index, self.istack, self.pdepth = new_state

parse_failed_sentinel = object()

class Parser(object):
    '''
    Parser
    ======
    
    '''
    def __init__(self,parser):
        self.parser = parser
    
    def _parse(self,stream):
        self.parser(stream)
    
    def __call__(self,stream):
        initial_state = stream.state
        
        memo_id = (self,initial_state)
        
        if memo_id in stream.callers:
            raise LeftRecursion(stream)
        
        if memo_id not in stream.memo:
            '"push" into call stack'
            stream.cstack.append(memo_id)
            stream.callers.add(memo_id)
            
            try:
                return_value = self._parse(stream)
                
            except ParseFailed:
                stream.memo[memo_id] = None, parse_failed_sentinel
                stream.state = initial_state
                raise
                
            else:
                stream.memo[memo_id] = stream.state, return_value
                
            finally:
                '"pop" out of call stack'
                stream.cstack.pop()
                stream.callers.remove(memo_id)
        
        new_state, return_value = stream.memo[memo_identifier]
        
        if return_value is parse_failed_sentinel:
            raise ParseFailed(stream)
            
        stream.state = new_state
        return return_value

class And(Parser):
    pass

class Regex(Parser):
    def __init__(self,regex):
        import re
        self.regex = re.compile(regex)
    
    def _parse(self,stream):
        match = self.regex.match(stream.string,stream.index)
        if match is None:
            raise ParseFailed()
        stream.index = match.end()
        return match.group()

without_newline = Regex(r'[ \t]+')
with_newline    = Regex(r'[ \t\n]+')

@Parser
def space(stream):
    return (with_newline if stream.pdepth else without_newline)(stream)

class Open(Parser):
    'Open parenthetical structure'
    def __init__(self,parser):
        self.parser = parser
    
    def _parse(self,stream):
        stream.depth += 1
        return self.parser(stream)

class Close(Parser):
    'Close parenthetical structure'
    def __init__(self,parser):
        self.parser = parser
    
    def _parse(self,stream):
        stream.depth -= 1
        if stream.pdepth < 0:
            raise MismatchedClosure(stream)
        return self.parser(stream)



