from abc import ABC, abstractmethod

from lexer.exceptions import LexerError


class BaseErrorHandler(ABC):
    @abstractmethod
    def handle_lexer_error(self, exception: LexerError):
        ...


class ErrorHandler(BaseErrorHandler):
    def handle_lexer_error(self, exception: LexerError):
        # line = exception.position.line
        # column = exception.position.column
        message = exception.message
        print(f"LexerError: {message}")
        # print(f"{line}:{column} | <code>")
