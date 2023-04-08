from abc import ABC, abstractmethod

from lexer.exceptions import LexerError


class BaseErrorHandler(ABC):
    @abstractmethod
    def handle_lexer_error(self, exception: LexerError):
        ...


class ErrorHandler(BaseErrorHandler):
    def handle_lexer_error(self, exception: LexerError):
        print(
            f"[{exception.line}:{exception.column}] Error: {exception.msg}"
        )
