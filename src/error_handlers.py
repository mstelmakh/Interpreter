from abc import ABC, abstractmethod

from lexer.exceptions import LexerError


class BaseErrorHandler(ABC):
    @abstractmethod
    def handle_lexer_error(self, exception: LexerError):
        ...


class ErrorHandler(BaseErrorHandler):

    def get_error_line(self, filename, byte_offset):
        with open(filename, "rb") as f:
            f.seek(byte_offset)
            line = f.readline().decode().rstrip()
        return line

    def handle_lexer_error(self, exception: LexerError):
        line = self.get_error_line(
                exception.position.filename,
                exception.position.offset
            ) if exception.position.filename else None
        line_n = exception.position.line
        column_n = exception.position.column
        message = exception.message
        print(f"LexerError: {message}")
        if line:
            print(f"   {line_n}:{column_n} | {line}")
