import pytest
from sys import maxsize

from lexer.lexers import Lexer, LexerWithoutComments
from lexer.streams import TextStream, Position
from lexer.tokens import (
    Token,
    TokenType,
    COMPOSITE_CHAR_MAP,
    SINGLE_CHAR_MAP,
    KEYWORDS_MAP
)
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


@pytest.mark.parametrize('text', (
        ' while', '=while', '//while', '5while',
        '"while"', '"string"while', '\nwhile'
        )
)
def test_try_build_ident_or_keyword_fail(text):
    lexer = create_lexer(text)

    assert lexer.try_build_ident_or_keyword() is False
    assert lexer.stream.current_char == text[0]
    assert lexer.token is None


@pytest.mark.parametrize('identifier', (
        "variable", "orchid", "String", "_String",
        "_St__53_63_ring___1"
))
def test_try_build_ident_or_keyword_ident(identifier: str):
    text = identifier + "=100"
    lexer = create_lexer(text)

    assert lexer.try_build_ident_or_keyword() is True
    assert lexer.stream.current_char == "="
    assert lexer.token is not None
    assert lexer.token.type == TokenType.IDENTIFIER
    assert lexer.token.value == identifier


@pytest.mark.parametrize('keyword, keyword_type', KEYWORDS_MAP.items())
def test_try_build_ident_or_keyword_keyword(
    keyword: str,
    keyword_type: TokenType
):
    text = keyword + "=100"
    lexer = create_lexer(text)

    assert lexer.try_build_ident_or_keyword() is True
    assert lexer.stream.current_char == "="
    assert lexer.token is not None
    assert lexer.token.type == keyword_type
    assert lexer.token.value is None


@pytest.mark.parametrize('text', (
        ' ', '=', '//', '5',
        '"str"', '\n', 'if'
    )
)
def test_try_build_eof_fail(text):
    lexer = create_lexer(text)

    assert lexer.try_build_eof() is False
    assert lexer.stream.current_char == text[0]
    assert lexer.token is None


def test_try_build_eof():
    text = 'a'
    lexer = create_lexer(text)
    lexer.stream.advance()
    assert lexer.try_build_eof() is True
    assert lexer.stream.current_char == ''
    assert lexer.token is not None
    assert lexer.token.type == TokenType.EOF
    assert lexer.token.value is None


@pytest.mark.parametrize('text, expected_token', (
    ('+ 55;', (
        Token(TokenType.PLUS, None, Position(1, 1, 0))
    )),
    ('// comment1', (
        Token(TokenType.COMMENT, ' comment1', Position(1, 1, 0))
    )),
    ('"string"=="a"', (
        Token(TokenType.STRING, "string", Position(1, 1, 0))
    )),
    ('005.156001+\n', (
        Token(TokenType.NUMBER, 5.156001, Position(1, 1, 0))
    )),
    ('variable%', (
        Token(TokenType.IDENTIFIER, 'variable', Position(1, 1, 0))
    )),
    ('var a = 5;', (
        Token(TokenType.VAR, None, Position(1, 1, 0))
    )),
    ('', (
        Token(TokenType.EOF, None, Position(1, 1, 0))
    )),
))
def test_get_next_token(text: str, expected_token: Token):
    lexer = create_lexer(text)

    assert lexer.next_token() is not None
    assert lexer.token is not None
    assert lexer.token == expected_token


@pytest.mark.parametrize('text, expected_token', (
    ('+ 55 // comment;', (
        Token(TokenType.PLUS, None, Position(1, 1, 0))
    )),
    ('// comment1 \n var', (
        Token(TokenType.VAR, None, Position(2, 2, 14))
    )),
    ('// "string1" \n // "string2" \n "string3"', (
        Token(TokenType.STRING, "string3", Position(3, 2, 30))
    ))
))
def test_comment_filter_get_next_token(text: str, expected_token: Token):
    lexer = create_lexer(text)
    filter = LexerWithoutComments(lexer)

    assert filter.next_token() is not None
    assert filter.token is not None
    assert filter.token == expected_token


TEST_TEXT_TOKENS_MAP = [
    (
        "€var a = 5; !\n"
        "const ^b = a / 10;",
        [
            Token(TokenType.VAR, None, Position(1, 2, 3)),
            Token(TokenType.IDENTIFIER, "a", Position(1, 6, 7)),
            Token(TokenType.EQUAL, None, Position(1, 8, 9)),
            Token(TokenType.NUMBER, 5, Position(1, 10, 11)),
            Token(TokenType.SEMICOLON, None, Position(1, 11, 12)),
            Token(TokenType.CONST, None, Position(2, 1, 16)),
            Token(TokenType.IDENTIFIER, "b", Position(2, 8, 23)),
            Token(TokenType.EQUAL, None, Position(2, 10, 25)),
            Token(TokenType.IDENTIFIER, "a", Position(2, 12, 27)),
            Token(TokenType.SLASH, None, Position(2, 14, 29)),
            Token(TokenType.NUMBER, 10, Position(2, 16, 31)),
            Token(TokenType.SEMICOLON, None, Position(2, 18, 33)),
            Token(TokenType.EOF, None, Position(2, 19, 34))
        ],
        [
            LexerError("Unexpected character: €", Position(1, 1, 0)),
            LexerError("Unexpected character: !", Position(1, 13, 14)),
            LexerError("Unexpected character: ^", Position(2, 7, 22)),
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
