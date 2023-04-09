from copy import copy

from lexer.tokens import (
    Token,
    TokenType,
    KEYWORDS_MAP,
    SINGLE_CHAR_MAP,
    COMPOSITE_CHAR_MAP,
    INDENTATION_CHARS,
    COMMENT_CHAR
)
from lexer.utils import is_digit, is_alpha, is_alphanumeric
from lexer.streams import Stream
from error_handlers import BaseErrorHandler
from lexer.exceptions import LexerError

from abc import ABC, abstractmethod


def print_error(line: int, column: int, message: str):
    print(f"Error at {line}:{column}: {message}")


class BaseScanner(ABC):

    @abstractmethod
    def next_token(self) -> Token:
        ...


class Scanner:
    def __init__(self, stream: Stream, error_handler: BaseErrorHandler):
        self.stream = stream
        self.error_handler = error_handler
        self.current_char = self.stream.advance()
        self.start_position = copy(stream.position)
        self.lexeme = ""
        self.token = None

    def error(self, message: str) -> None:
        self.token = None
        error = LexerError(message, self.start_position)
        self.error_handler.handle_lexer_error(error)

    def try_build_string(self) -> bool:
        if not self.current_char == '"':
            return False
        self.current_char = self.stream.advance()
        value = []
        while self.current_char and not self.current_char == '"':
            if self.current_char == "\\":
                self.current_char = self.stream.advance()
                if self.current_char == "n":
                    value.append("\n")
                elif self.current_char == "b":
                    value.append("\b")
                elif self.current_char == "r":
                    value.append("\r")
                elif self.current_char == "t":
                    value.append("\t")
                elif self.current_char == "\\":
                    value.append("\\")
                elif self.current_char == "\"":
                    value.append("\"")
                else:
                    self.error(
                        f"Invalid escape character: '\\{self.current_char}'"
                    )
            else:
                value.append(self.current_char)
            self.current_char = self.stream.advance()
        if not self.current_char:
            self.error("Unterminated string.")
            return True
        if self.current_char == '"':
            self.current_char = self.stream.advance()
        self.token = self.create_token(TokenType.STRING, "".join(value))
        return True

    def try_build_number(self) -> bool:
        if not is_digit(self.current_char):
            return False
        integer = 0
        fraction = 0.0
        fraction_length = 0
        while is_digit(self.current_char):
            integer = integer * 10 + int(self.current_char)
            self.current_char = self.stream.advance()

        if self.current_char == '.':
            self.current_char = self.stream.advance()
            while is_digit(self.current_char):
                fraction = fraction * 10 + int(self.current_char)
                fraction_length += 1
                self.current_char = self.stream.advance()
        if fraction_length > 0:
            fraction = fraction / (10 ** fraction_length)
        self.token = self.create_token(
            TokenType.NUMBER,
            integer + fraction
        )
        return True

    def try_build_ident_or_keyword(self) -> bool:
        if not is_alpha(self.current_char):
            return False
        value = []
        while is_alphanumeric(self.current_char):
            value.append(self.current_char)
            self.current_char = self.stream.advance()
        value_str = "".join(value)
        if value_str in KEYWORDS_MAP:
            self.token = self.create_token(KEYWORDS_MAP[value_str])
        else:
            self.token = self.create_token(
                TokenType.IDENTIFIER,
                value_str
            )
        return True

    def build_comment(self) -> Token:
        value = []
        while self.current_char and not self.current_char == "\n":
            value.append(self.current_char)
            self.current_char = self.stream.advance()
        return self.create_token(TokenType.COMMENT, "".join(value))

    def try_build_operator_or_comment(self) -> bool:
        is_beginning_of_composite = (
            self.current_char
            in [string[0] for string in COMPOSITE_CHAR_MAP.keys()]
        )
        is_beginning_of_comment = self.current_char == COMMENT_CHAR[0]
        if not (self.current_char in SINGLE_CHAR_MAP
                or is_beginning_of_composite):
            return False
        if not (is_beginning_of_composite or is_beginning_of_comment):
            self.token = self.create_token(
                SINGLE_CHAR_MAP[self.current_char],
                None
            )
            self.current_char = self.stream.advance()
            return True
        previous = self.current_char
        self.current_char = self.stream.advance()
        lexeme = previous + self.current_char
        if lexeme == COMMENT_CHAR:
            self.current_char = self.stream.advance()
            self.token = self.build_comment()
        elif lexeme in COMPOSITE_CHAR_MAP:
            self.token = self.create_token(COMPOSITE_CHAR_MAP[lexeme])
            self.current_char = self.stream.advance()
        elif previous in SINGLE_CHAR_MAP:
            # If the first character was the beginning of the composite
            # operator, but the second character didn't match.
            # For example if '=' and '==' are operators, but we have '=-'
            self.token = self.create_token(SINGLE_CHAR_MAP[previous])
        else:
            # If started as a composite operator, but didn't match any
            # and is not a single char operator
            self.error(f"Unexpected character: {previous}")
            return True
        return True

    def try_build_eof(self) -> bool:
        if not self.current_char:
            self.token = self.create_token(TokenType.EOF)
            return True
        return False

    def skip_whitespaces(self) -> None:
        while self.current_char in INDENTATION_CHARS:
            self.current_char = self.stream.advance()

    def next_token(self) -> Token | None:
        funcs = (
            self.try_build_operator_or_comment,
            self.try_build_string,
            self.try_build_number,
            self.try_build_ident_or_keyword,
            self.try_build_eof
        )
        self.skip_whitespaces()
        self.start_position = copy(self.stream.position)
        for func in funcs:
            if func():
                return self.token

        self.token = None
        self.error(f"Unexpected character: {self.current_char}")
        self.current_char = self.stream.advance()
        return None

    def create_token(
        self,
        token_type: TokenType,
        value: int | float | str | None = None
    ) -> None:
        return Token(token_type, value, self.start_position)


class ScannerWithoutComments(BaseScanner):
    def __init__(self, scanner: Scanner):
        self.scanner = scanner

    def next_token(self) -> Token:
        token = self.scanner.next_token()
        while token and token.type == TokenType.COMMENT:
            token = self.scanner.next_token()
        self.token = self.scanner.token
        return self.token
