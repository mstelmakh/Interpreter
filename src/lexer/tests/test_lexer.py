import pytest

from lexer.lexers import Lexer
from lexer.streams import TextStream, Position
from lexer.tokens import Token, TokenType
from lexer.exceptions import LexerError
from lexer.tests.utils import get_all_tokens, DebugErrorHandler, create_lexer


TEST_TEXT_TOKENS_MAP = [
    (
        "var a = 5; !\n"
        "const !b = a / 10;",
        [
            Token(TokenType.VAR, None, Position(1, 1, 0)),
            Token(TokenType.IDENTIFIER, "a", Position(1, 5, 4)),
            Token(TokenType.EQUAL, None, Position(1, 7, 6)),
            Token(TokenType.NUMBER, 5, Position(1, 9, 8)),
            Token(TokenType.SEMICOLON, None, Position(1, 10, 9)),
            Token(TokenType.CONST, None, Position(2, 1, 13)),
            Token(TokenType.IDENTIFIER, "b", Position(2, 8, 20)),
            Token(TokenType.EQUAL, None, Position(2, 10, 22)),
            Token(TokenType.IDENTIFIER, "a", Position(2, 12, 24)),
            Token(TokenType.SLASH, None, Position(2, 14, 26)),
            Token(TokenType.NUMBER, 10, Position(2, 16, 28)),
            Token(TokenType.SEMICOLON, None, Position(2, 18, 30)),
            Token(TokenType.EOF, None, Position(2, 19, 31))
        ],
        [
            LexerError("Unexpected character: !", Position(1, 12, 11)),
            LexerError("Unexpected character: !", Position(2, 7, 19)),
        ]
    ),
]


@pytest.mark.parametrize("text, tokens, errors", TEST_TEXT_TOKENS_MAP)
def test_lexer(text: str, tokens: list[Token], errors: list[LexerError]):
    stream = TextStream(text)
    error_handler = DebugErrorHandler()
    lexer = Lexer(stream, error_handler)

    assert get_all_tokens(lexer) == tokens
    assert error_handler.errors == errors


def test_skip_whitespaces():
    text = "\t     \t\n  \r  abc"
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "\t"
    lexer.skip_whitespaces()
    assert lexer.stream.current_char == "a"
    lexer.skip_whitespaces()
    assert lexer.stream.current_char == "a"


def test_try_build_operator_or_comment_fail():
    text = "hello"
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "h"
    assert lexer.token is None
    assert lexer.try_build_operator_or_comment() is False
    assert lexer.stream.current_char == "h"
    assert lexer.token is None


def test_try_build_operator_or_comment_plus():
    text = "+abcdef"
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "+"
    assert lexer.token is None
    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.PLUS
    assert lexer.token.value is None


def test_try_build_operator_or_comment_slash():
    text = "/abcdef"
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "/"
    assert lexer.token is None
    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.SLASH
    assert lexer.token.value is None


def test_try_build_operator_or_comment_part_of_composite():
    text = "=abcdef"
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "="
    assert lexer.token is None
    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.EQUAL
    assert lexer.token.value is None


def test_try_build_operator_or_comment_part_of_composite_error():
    text = "!abcdef"
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "!"
    assert lexer.token is None
    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is None
    assert len(lexer.error_handler.errors) == 1
    assert lexer.error_handler.errors == [
        LexerError("Unexpected character: !", Position(1, 1, 0))
    ]


def test_try_build_operator_or_comment_composite():
    text = "<=abcdef"
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "<"
    assert lexer.token is None
    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.LESS_EQUAL
    assert lexer.token.value is None


def test_try_build_operator_or_comment_comment():
    text = '//ab"e\tf'
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "/"
    assert lexer.token is None
    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == ""
    assert lexer.token is not None
    assert lexer.token.type == TokenType.COMMENT
    assert lexer.token.value == 'ab"e\tf'


def test_try_build_operator_or_comment_comment_with_newline():
    text = '//ab"e\tf\nafter'
    lexer = create_lexer(text)

    assert lexer.stream.current_char == "/"
    assert lexer.token is None
    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "\n"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.COMMENT
    assert lexer.token.value == 'ab"e\tf'
