import pytest

from lexer.streams import TextStream, Position
from lexer.scanner import Scanner
from lexer.tests.utils import get_all_tokens, DebugErrorHandler
from lexer.tokens import Token, TokenType
from lexer.exceptions import LexerError


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
def test_identifier(text: str, tokens: list[Token], errors: list[LexerError]):
    stream = TextStream(text)
    error_handler = DebugErrorHandler()
    scanner = Scanner(stream, error_handler)

    assert get_all_tokens(scanner) == tokens
    assert error_handler.errors == errors
