class LexerError(SyntaxError):
    def __init__(self, line, column, message):
        super().__init__(message)
        self.line = line
        self.column = column
