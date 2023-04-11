import pytest
from sys import maxsize

from lexer.lexers import Lexer
from lexer.streams import TextStream, Position
from lexer.tokens import Token, TokenType, COMPOSITE_CHAR_MAP, SINGLE_CHAR_MAP
from lexer.exceptions import LexerError
from lexer.tests.utils import get_all_tokens, DebugErrorHandler, create_lexer


def test_init_lexer():
    text = "var a = 5;"
    stream = TextStream(text)
    error_handler = DebugErrorHandler()
    lexer = Lexer(stream, error_handler)
    assert lexer.stream.current_char == "v"
    assert lexer.token is None


@pytest.mark.parametrize('ident', (
        '\t     \t\n  \r ', '\r \t \n    ',
        '\r\r\r', '   \n\r\t', ''
))
def test_skip_whitespaces(ident):
    text = ident + "abc"
    lexer = create_lexer(text)

    lexer.skip_whitespaces()
    assert lexer.stream.current_char == "a"
    lexer.skip_whitespaces()
    assert lexer.stream.current_char == "a"


@pytest.mark.parametrize('text', (
        'a+-=*', '"string"+-=*', '5+-=*',
        ' +-=*', 'fn+-=*', '\n+-=*'
        )
)
def test_try_build_operator_or_comment_fail(text: str):
    lexer = create_lexer(text)

    assert lexer.try_build_operator_or_comment() is False
    assert lexer.stream.current_char == text[0]
    assert lexer.token is None


@pytest.mark.parametrize('operator, token_type', SINGLE_CHAR_MAP.items())
def test_try_build_operator_or_comment_single_char(
    operator: str,
    token_type: TokenType
):
    text = operator + "abcdef"
    lexer = create_lexer(text)

    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == token_type
    assert lexer.token.value is None


def test_try_build_operator_or_comment_slash():
    text = "/abcdef"
    lexer = create_lexer(text)

    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.SLASH
    assert lexer.token.value is None


def test_try_build_operator_or_comment_part_of_composite():
    text = "=abcdef"
    lexer = create_lexer(text)

    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.EQUAL
    assert lexer.token.value is None


def test_try_build_operator_or_comment_part_of_composite_error():
    text = "!abcdef"
    lexer = create_lexer(text)

    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is None
    assert len(lexer.error_handler.errors) == 1
    assert lexer.error_handler.errors == [
        LexerError("Unexpected character: !", Position(1, 1, 0))
    ]


@pytest.mark.parametrize('operator, token_type', COMPOSITE_CHAR_MAP.items())
def test_try_build_operator_or_comment_composite(
    operator: str,
    token_type: TokenType
):
    text = operator + "a-c$e\n"
    lexer = create_lexer(text)

    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == token_type
    assert lexer.token.value is None


def test_try_build_operator_or_comment_comment():
    text = '//ab"e\tf'
    lexer = create_lexer(text)

    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == ""
    assert lexer.token is not None
    assert lexer.token.type == TokenType.COMMENT
    assert lexer.token.value == 'ab"e\tf'


def test_try_build_operator_or_comment_comment_with_newline():
    text = '//ab"e\tf\nafter'
    lexer = create_lexer(text)

    assert lexer.try_build_operator_or_comment() is True
    assert lexer.stream.current_char == "\n"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.COMMENT
    assert lexer.token.value == 'ab"e\tf'


@pytest.mark.parametrize('text', (
        'a"string"', '="string"', '//"string"', '5"string"',
        ' "string"', 'fn"string"', '\n"string"'
        )
)
def test_try_build_string_fail(text):
    lexer = create_lexer(text)

    assert lexer.try_build_string() is False
    assert lexer.stream.current_char == text[0]
    assert lexer.token is None


@pytest.mark.parametrize('string_value', (
        "text", "53+52", "'text'", "%^&!2", "\nabc\t\n"
))
def test_try_build_string_normal(string_value: str):
    text = '"' + string_value + '"' + "after"
    lexer = create_lexer(text)

    assert lexer.try_build_string() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.STRING
    assert lexer.token.value == string_value


@pytest.mark.parametrize('string_value, expected', (
        ("str\\ning", "str\ning"),
        ('str\\"ing', 'str\"ing'),
        ('st\\br\\bing', 'st\br\bing'),
        ('st\\tr\\ting', 'st\tr\ting'),
        ('\\bstr\\ring\\r', '\bstr\ring\r'),
        ('\\\\str\\\\ing\\\\', '\\str\\ing\\'),
))
def test_try_build_string_with_escape_character(
    string_value: str,
    expected: str
):
    text = '"' + string_value + '"' + 'after'
    lexer = create_lexer(text)

    assert lexer.try_build_string() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.STRING
    assert lexer.token.value == expected


def test_try_build_string_with_invalid_escape_character():
    text = '"\\ws\\%t\\@r\\:ing"after'
    lexer = create_lexer(text)

    assert lexer.try_build_string() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.STRING
    assert lexer.token.value == "string"
    assert len(lexer.error_handler.errors) == 4
    assert lexer.error_handler.errors == [
        LexerError("Invalid escape character: '\\w'", Position(1, 2, 1)),
        LexerError("Invalid escape character: '\\%'", Position(1, 5, 4)),
        LexerError("Invalid escape character: '\\@'", Position(1, 8, 7)),
        LexerError("Invalid escape character: '\\:'", Position(1, 11, 10)),
    ]


@pytest.mark.parametrize('string_value', (
    "unterminated", "^&\\nhello\n", 'string\\" // also string\n\r\\rnew line'
))
def test_try_build_string_unterminated(string_value: str):
    text = '"' + string_value
    lexer = create_lexer(text)

    assert lexer.try_build_string() is True
    # Reads till the end
    assert lexer.stream.current_char == ""
    assert lexer.token is None
    assert len(lexer.error_handler.errors) == 1
    assert lexer.error_handler.errors == [
        LexerError("Unterminated string.", Position(1, 1, 0))
    ]


@pytest.mark.parametrize('text', (
    'a52.14+5', '=52.14+5', '//52.14+5', '"string"52.14+5',
    ' 52.14+5', 'fn52.14+5', '\n52.14+5', '"52.14+5"'
))
def test_try_build_number_fail(text: str):
    lexer = create_lexer(text)

    assert lexer.try_build_number() is False
    assert lexer.stream.current_char == text[0]
    assert lexer.token is None


@pytest.mark.parametrize('text', (
    '10', '0', '00001005', str(maxsize * 2 + 1 + 100),
))
def test_try_build_number_integer(text: str):
    lexer = create_lexer(text + "after")

    assert lexer.try_build_number() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.NUMBER
    assert lexer.token.value == int(text)


@pytest.mark.parametrize('text', (
    '10.0', '0.0', '3.999999', '000000501.503', '000015.',
    str(maxsize * 2 + 1 + 100) + '.' + str(maxsize * 2 + 1 + 100),
))
def test_try_build_number_float(text: str):
    lexer = create_lexer(text + "after")

    assert lexer.try_build_number() is True
    assert lexer.stream.current_char == "a"
    assert lexer.token is not None
    assert lexer.token.type == TokenType.NUMBER
    assert lexer.token.value == float(text)


def test_try_build_ident_or_keyword_fail():
    pass


def test_try_build_ident_or_keyword_ident():
    pass


def test_try_build_ident_or_keyword_keyword():
    pass


def test_try_build_eof_fail():
    pass


def test_try_build_eof():
    pass


def test_get_next_token():
    pass


def test_comment_filter_get_next_token():
    pass


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
