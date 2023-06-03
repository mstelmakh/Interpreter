from abc import ABC, abstractmethod

from lexer.exceptions import LexerError
from parser.exceptions import ParserError
from interpreter.exceptions import RuntimeError


class BaseErrorHandler(ABC):
    @abstractmethod
    def handle_lexer_error(self, exception: LexerError):
        ...

    @abstractmethod
    def handle_parser_error(self, exception: ParserError):
        ...

    @abstractmethod
    def handle_runtime_error(self, exception: RuntimeError):
        ...


class ErrorHandler(BaseErrorHandler):

    def get_error_line(self, filename, line_n):
        with open(filename, "r") as f:
            lines = f.readlines()
        return lines[line_n - 1].strip()

    def print_error(self, exception):
        line = self.get_error_line(
            exception.position.filename,
            exception.position.line
        ) if exception.position.filename else None
        line_n = exception.position.line
        column_n = exception.position.column
        print(f"{exception.__class__.__name__}: {exception}")
        if line:
            print(f"   {line_n}:{column_n} | {line}")

    def handle_lexer_error(self, exception: LexerError):
        self.print_error(exception)

    def handle_parser_error(self, exception: ParserError):
        self.print_error(exception)

    def handle_runtime_error(self, exception: RuntimeError):
        self.print_error(exception)
