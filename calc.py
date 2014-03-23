from parse import Parser, SingletonParser, RegexParser

whitespace_parser = RegexParser(r'\s+')

class TokenParser(Parser):
    '''
    Tokens are regexes that are optionally preceded by whitespace
    '''
    def __init__(self,regex):
        self.regex_parser = RegexParser(regex)
    
    def _parse(self,stream):
        try:
            whitespace_parser.parse(stream)
        except ParseFailed:
            pass
        
        return self.regex_parser.parse(stream)

@SingletonParser
def integer_parser(stream):
    pass



