import pytest

from lexer.streams import TextStream
from lexer.scanner import Scanner
from lexer.tests.utils import get_all_tokens, DebugErrorHandler
from lexer.tokens import Token, TokenType
from lexer.exceptions import LexerError


TEST_TEXT_TOKENS_MAP = [
    (
        "var a = 5; ^\n"
        "const b = a / 10;",
        [
            Token(TokenType.VAR, None, 1),
            Token(TokenType.IDENTIFIER, "a", 1),
            Token(TokenType.EQUAL, None, 1),
            Token(TokenType.NUMBER, 5, 1),
            Token(TokenType.SEMICOLON, None, 1),
            Token(TokenType.CONST, None, 2),
            Token(TokenType.IDENTIFIER, "b", 2),
            Token(TokenType.EQUAL, None, 2),
            Token(TokenType.IDENTIFIER, "a", 2),
            Token(TokenType.SLASH, None, 2),
            Token(TokenType.NUMBER, 10, 2),
            Token(TokenType.SEMICOLON, None, 2),
            Token(TokenType.EOF, None, 2)
        ],
        [
            LexerError(1, 12, "Unexpected character: ^")
        ]
    ),
]


@pytest.mark.parametrize("text, tokens, errors", TEST_TEXT_TOKENS_MAP)
def test_identifier(text: str, tokens: list[Token], errors: list[LexerError]):
    stream = TextStream(text)
    error_handler = DebugErrorHandler()
    scanner = Scanner(stream, error_handler)

    assert get_all_tokens(scanner) == tokens
    assert error_handler.errors == errors
