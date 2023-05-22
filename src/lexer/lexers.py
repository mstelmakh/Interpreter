from copy import copy

from lexer.tokens import (
    Token,
    TokenType,
    KEYWORDS_MAP,
    SINGLE_CHAR_MAP,
    COMPOSITE_CHAR_MAP,
    ESCAPE_SEQUENCE_MAP,
    INDENTATION_CHARS,
    COMMENT_CHAR
)
from lexer.utils import is_digit, is_letter, is_alphanumeric
from lexer.streams import Stream
from lexer.exceptions import (
    UnexpecterCharacterError,
    UnterminatedStringError,
    InvalidEscapeSequenceError
)

from abc import ABC, abstractmethod


class BaseLexer(ABC):

    @abstractmethod
    def next_token(self) -> Token:
        ...


class Lexer(BaseLexer):
    def __init__(self, stream: Stream):
        self.stream = stream

        self.stream.advance()
        self.lexeme_start_pos = copy(self.stream.position)

    def try_build_string(self) -> bool:
        if not self.stream.current_char == '"':
            return None
        self.stream.advance()
        value = []
        while self.stream.current_char and not self.stream.current_char == '"':
            if self.stream.current_char == "\\":
                position = copy(self.stream.position)
                self.stream.advance()
                if self.stream.current_char == "":
                    raise UnterminatedStringError(self.lexeme_start_pos)
                escape_sequence = '\\' + self.stream.current_char
                if escape_sequence in ESCAPE_SEQUENCE_MAP:
                    value.append(ESCAPE_SEQUENCE_MAP[escape_sequence])
                else:
                    raise InvalidEscapeSequenceError(
                        sequence=self.stream.current_char,
                        position=position
                    )
            else:
                value.append(self.stream.current_char)
            self.stream.advance()
        self.ensureNotEOF(UnterminatedStringError)
        if self.stream.current_char == '"':
            self.stream.advance()
        return self.create_token(TokenType.STRING, "".join(value))

    def _parse_integer(self) -> tuple[int, int]:
        integer, length = 0, 0
        while is_digit(self.stream.current_char):
            integer = integer * 10 + int(self.stream.current_char)
            length += 1
            self.stream.advance()
        return integer, length

    def try_build_number(self) -> bool:
        # Allows leading zeros and float number without float part
        # For example: 000015.5 = 15.5, 15. = 15.0
        if not is_digit(self.stream.current_char):
            return None
        integer = 0
        fraction = 0.0
        fraction_length = 0
        is_float = False
        integer, _ = self._parse_integer()
        while is_digit(self.stream.current_char):
            integer = integer * 10 + int(self.stream.current_char)
            self.stream.advance()
        if self.stream.current_char == '.':
            is_float = True
            self.stream.advance()
            fraction, fraction_length = self._parse_integer()
        if fraction_length > 0:
            fraction = fraction / (10 ** fraction_length)
        return self.create_token(
            TokenType.NUMBER,
            integer + fraction if is_float else integer
        )

    def try_build_ident_or_keyword(self) -> bool:
        if not is_letter(self.stream.current_char):
            return None
        value = []
        while is_alphanumeric(self.stream.current_char):
            value.append(self.stream.current_char)
            self.stream.advance()
        value_str = "".join(value)
        if value_str in KEYWORDS_MAP:
            return self.create_token(KEYWORDS_MAP[value_str])
        return self.create_token(
            TokenType.IDENTIFIER,
            value_str
        )

    def _is_beginning_of_composite_operator_or_comment(self) -> bool:
        char = self.stream.current_char
        return (
            char in [string[0] for string in COMPOSITE_CHAR_MAP.keys()]
            or char == COMMENT_CHAR[0]
        )

    def try_build_operator_or_comment(self) -> bool:
        is_single_char_operator = self.stream.current_char in SINGLE_CHAR_MAP
        is_beginning_of_composite_or_comment = \
            self._is_beginning_of_composite_operator_or_comment()
        if not (is_single_char_operator or
                is_beginning_of_composite_or_comment
                ):
            return None
        if not is_beginning_of_composite_or_comment:
            token = self.create_token(
                SINGLE_CHAR_MAP[self.stream.current_char]
            )
            self.stream.advance()
            return token
        previous = self.stream.current_char
        self.stream.advance()
        lexeme = previous + self.stream.current_char
        if lexeme == COMMENT_CHAR:
            self.stream.advance()
            value = []
            while (
                self.stream.current_char and
                not self.stream.current_char == "\n"
            ):
                value.append(self.stream.current_char)
                self.stream.advance()
            token = self.create_token(TokenType.COMMENT, "".join(value))
        elif lexeme in COMPOSITE_CHAR_MAP:
            token = self.create_token(COMPOSITE_CHAR_MAP[lexeme])
            self.stream.advance()
        elif previous in SINGLE_CHAR_MAP:
            # If the first character was the beginning of the composite
            # operator, but the second character didn't match.
            # For example if '=' and '==' are operators, but we have '=-'
            token = self.create_token(SINGLE_CHAR_MAP[previous])
        else:
            # If started as a composite operator, but didn't match any
            # and is not a single char operator
            raise UnexpecterCharacterError(
                character=previous,
                position=self.lexeme_start_pos
            )
        return token

    def try_build_eof(self) -> bool:
        if not self.stream.current_char:
            return self.create_token(TokenType.EOF)
        return None

    def skip_whitespaces(self) -> None:
        while self.stream.current_char in INDENTATION_CHARS:
            self.stream.advance()

    def next_token(self) -> Token | None:
        funcs = (
            self.try_build_operator_or_comment,
            self.try_build_string,
            self.try_build_number,
            self.try_build_ident_or_keyword,
            self.try_build_eof
        )
        self.skip_whitespaces()
        self.lexeme_start_pos = copy(self.stream.position)
        for func in funcs:
            token = func()
            if token:
                return token

        raise UnexpecterCharacterError(
            character=self.stream.current_char,
            position=self.lexeme_start_pos
        )

    def ensureNotEOF(self, ErrorType):
        if not self.stream.current_char:
            raise ErrorType(self.lexeme_start_pos)

    def create_token(
        self,
        token_type: TokenType,
        value: int | float | str | None = None
    ) -> None:
        return Token(token_type, value, self.lexeme_start_pos)


class LexerWithoutComments(BaseLexer):
    def __init__(self, lexer: Lexer):
        self.lexer = lexer

    def next_token(self) -> Token:
        token = self.lexer.next_token()
        while token and token.type == TokenType.COMMENT:
            token = self.lexer.next_token()
        return token
