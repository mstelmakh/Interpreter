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
from lexer.exceptions import (
    UnexpecterCharacterError,
    UnterminatedStringError,
    InvalidEscapeSequenceError
)
from lexer.tests.utils import (
    get_all_tokens,
    create_lexer,
    get_single_char_operators_beginning_of_composite
)


def test_init_lexer():
    text = "var a = 5;"
    stream = TextStream(text)
    lexer = Lexer(stream)
    assert lexer.stream.current_char == "v"


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

    token = lexer.try_build_operator_or_comment()

    assert token is None
    assert lexer.stream.current_char == text[0]


@pytest.mark.parametrize('operator, token_type', SINGLE_CHAR_MAP.items())
def test_try_build_operator_or_comment_single_char(
    operator: str,
    token_type: TokenType
):
    text = operator + "abcdef"
    lexer = create_lexer(text)

    token = lexer.try_build_operator_or_comment()

    assert token is not None
    assert lexer.stream.current_char == "a"
    assert token.type == token_type
    assert token.value is None


def test_try_build_operator_or_comment_slash():
    text = "/abcdef"
    lexer = create_lexer(text)

    token = lexer.try_build_operator_or_comment()

    assert token is not None
    assert lexer.stream.current_char == "a"
    assert token.type == TokenType.SLASH
    assert token.value is None


@pytest.mark.parametrize(
        'char, token_type', get_single_char_operators_beginning_of_composite()
)
def test_try_build_operator_or_comment_part_of_composite(char, token_type):
    text = char + "abcdef"
    lexer = create_lexer(text)

    token = lexer.try_build_operator_or_comment()

    assert token is not None
    assert lexer.stream.current_char == "a"
    assert token.type == token_type
    assert token.value is None


def test_try_build_operator_or_comment_part_of_composite_error():
    text = "!abcdef"
    lexer = create_lexer(text)

    with pytest.raises(UnexpecterCharacterError) as e:
        lexer.try_build_operator_or_comment()

    assert str(e.value) == "Unexpected character: `!`"
    assert e.value.position == Position(1, 1, 0)


@pytest.mark.parametrize('operator, token_type', COMPOSITE_CHAR_MAP.items())
def test_try_build_operator_or_comment_composite(
    operator: str,
    token_type: TokenType
):
    text = operator + "a-c$e\n"
    lexer = create_lexer(text)

    token = lexer.try_build_operator_or_comment()

    assert token is not None
    assert lexer.stream.current_char == "a"
    assert token.type == token_type
    assert token.value is None


def test_try_build_operator_or_comment_comment():
    text = '//ab"e\tf'
    lexer = create_lexer(text)

    token = lexer.try_build_operator_or_comment()

    assert token is not None
    assert lexer.stream.current_char == ""
    assert token.type == TokenType.COMMENT
    assert token.value == 'ab"e\tf'


def test_try_build_operator_or_comment_comment_with_newline():
    text = '//ab"e\tf\nafter'
    lexer = create_lexer(text)

    token = lexer.try_build_operator_or_comment()

    assert token is not None
    assert lexer.stream.current_char == "\n"
    assert token.type == TokenType.COMMENT
    assert token.value == 'ab"e\tf'


@pytest.mark.parametrize('text', (
        'a"string"', '="string"', '//"string"', '5"string"',
        ' "string"', 'fn"string"', '\n"string"'
        )
)
def test_try_build_string_fail(text):
    lexer = create_lexer(text)

    token = lexer.try_build_string()

    assert token is None
    assert lexer.stream.current_char == text[0]


@pytest.mark.parametrize('string_value', (
        "text", "53+52", "'text'", "%^&!2", "\nabc\t\n"
))
def test_try_build_string_normal(string_value: str):
    text = '"' + string_value + '"' + "after"
    lexer = create_lexer(text)

    token = lexer.try_build_string()

    assert token is not None
    assert lexer.stream.current_char == "a"
    assert token.type == TokenType.STRING
    assert token.value == string_value


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

    token = lexer.try_build_string()

    assert token is not None
    assert lexer.stream.current_char == "a"
    assert token.type == TokenType.STRING
    assert token.value == expected


@pytest.mark.parametrize('text, invalid_char, position', (
        ('"s\\%tring"', '\\%', Position(1, 3, 2)),
        ('"s\nt\\$ring"', '\\$', Position(2, 2, 4)),
        ('"s\nt\\rring\\a"', '\\a', Position(2, 8, 10)),
))
def test_try_build_string_with_invalid_escape_character(
    text: str, invalid_char: str, position: Position
):
    lexer = create_lexer(text)

    with pytest.raises(InvalidEscapeSequenceError) as e:
        lexer.try_build_string()

    assert str(e.value) == f"Invalid escape character: '{invalid_char}'"
    assert e.value.position == position


@pytest.mark.parametrize('string_value', (
    "unterminated", "^&\\nhello\n", 'string\\" // also string\n\r\\rnew line'
))
def test_try_build_string_unterminated(string_value: str):
    text = '"' + string_value
    lexer = create_lexer(text)

    with pytest.raises(UnterminatedStringError) as e:
        lexer.try_build_string()

    assert str(e.value) == "Unterminated string"
    assert e.value.position == Position(1, 1, 0)


@pytest.mark.parametrize('text', (
    'a52.14+5', '=52.14+5', '//52.14+5', '"string"52.14+5',
    ' 52.14+5', 'fn52.14+5', '\n52.14+5', '"52.14+5"'
))
def test_try_build_number_fail(text: str):
    lexer = create_lexer(text)

    token = lexer.try_build_number()

    assert lexer.stream.current_char == text[0]
    assert token is None


@pytest.mark.parametrize('text', (
    '10', '0', '00001005', str(maxsize * 2 + 1 + 100),
))
def test_try_build_number_integer(text: str):
    lexer = create_lexer(text + "after")

    token = lexer.try_build_number()

    assert token is not None
    assert lexer.stream.current_char == "a"
    assert token.type == TokenType.NUMBER
    assert token.value == int(text)


@pytest.mark.parametrize('text', (
    '10.0', '0.0', '3.999999', '000000501.503', '000015.',
    str(maxsize * 2 + 1 + 100) + '.' + str(maxsize * 2 + 1 + 100),
))
def test_try_build_number_float(text: str):
    lexer = create_lexer(text + "after")

    token = lexer.try_build_number()

    assert token is not None
    assert lexer.stream.current_char == "a"
    assert token.type == TokenType.NUMBER
    assert token.value == float(text)


@pytest.mark.parametrize('text', (
        ' while', '=while', '//while', '5while',
        '"while"', '"string"while', '\nwhile'
        )
)
def test_try_build_ident_or_keyword_fail(text):
    lexer = create_lexer(text)

    token = lexer.try_build_ident_or_keyword()

    assert lexer.stream.current_char == text[0]
    assert token is None


@pytest.mark.parametrize('identifier', (
        "variable", "orchid", "String", "_String",
        "_St__53_63_ring___1"
))
def test_try_build_ident_or_keyword_ident(identifier: str):
    text = identifier + "=100"
    lexer = create_lexer(text)

    token = lexer.try_build_ident_or_keyword()

    assert token is not None
    assert lexer.stream.current_char == "="
    assert token.type == TokenType.IDENTIFIER
    assert token.value == identifier


@pytest.mark.parametrize('keyword, keyword_type', KEYWORDS_MAP.items())
def test_try_build_ident_or_keyword_keyword(
    keyword: str,
    keyword_type: TokenType
):
    text = keyword + "=100"
    lexer = create_lexer(text)

    token = lexer.try_build_ident_or_keyword()

    assert token is not None
    assert lexer.stream.current_char == "="
    assert token.type == keyword_type
    assert token.value is None


@pytest.mark.parametrize('text', (
        ' ', '=', '//', '5',
        '"str"', '\n', 'if'
    )
)
def test_try_build_eof_fail(text):
    lexer = create_lexer(text)

    token = lexer.try_build_eof()

    assert lexer.stream.current_char == text[0]
    assert token is None


def test_try_build_eof():
    text = 'a'
    lexer = create_lexer(text)
    lexer.stream.advance()

    token = lexer.try_build_eof()

    assert token is not None
    assert lexer.stream.current_char == ''
    assert token.type == TokenType.EOF
    assert token.value is None


@pytest.mark.parametrize('text, token_type, value', tuple(
        (k, v, None) for k, v in
        (SINGLE_CHAR_MAP | COMPOSITE_CHAR_MAP | KEYWORDS_MAP).items()
    ) + (
        ('"string"', TokenType.STRING, "string"),
        ('00156.', TokenType.NUMBER, 156.0),
        ('variable', TokenType.IDENTIFIER, "variable"),
        ('', TokenType.EOF, None),
    )
)
def test_get_next_token(
    text: str,
    token_type: TokenType,
    value: int | float | str | None
):
    lexer = create_lexer(text)

    token = lexer.next_token()

    assert token is not None
    assert token.type == token_type
    assert token.value == value


@pytest.mark.parametrize('character', (
        '%', '$', '@', '!', '#', ']', '[', '&', "'", '`', '~',
        'ą', 'ę', 'ó', 'ł', 'ż', 'ź', 'ć',
))
def test_get_next_token_unexpecter_char_error(
    character: str
):
    lexer = create_lexer(character)

    with pytest.raises(UnexpecterCharacterError) as e:
        lexer.next_token()

    assert e.value.position == Position(1, 1, 0)
    assert str(e.value) == f"Unexpected character: `{character}`"


@pytest.mark.parametrize('string_value', (
        'string', 'str\\ning', '\\"\\nłć$\\n', 'string\\'
))
def test_get_next_token_unterminated_string_error(
    string_value: str
):
    lexer = create_lexer('"' + string_value)

    with pytest.raises(UnterminatedStringError) as e:
        lexer.next_token()

    assert e.value.position == Position(1, 1, 0)
    assert str(e.value) == 'Unterminated string'


@pytest.mark.parametrize('sequence', (
        '\\$', '\\#', '\\a', '\\g', "\\'"
))
def test_get_next_token_invalid_escape_sequence_error(
    sequence: str
):
    lexer = create_lexer('"pre' + sequence + 'post"')

    with pytest.raises(InvalidEscapeSequenceError) as e:
        lexer.next_token()

    assert e.value.position == Position(1, 5, 4)
    assert str(e.value) == f"Invalid escape character: '{sequence}'"


@pytest.mark.parametrize('text, token_type, value', tuple(
        (k, v, None) for k, v in
        (SINGLE_CHAR_MAP | COMPOSITE_CHAR_MAP | KEYWORDS_MAP).items()
    ) + (
        ('"string"', TokenType.STRING, "string"),
        ('00156.', TokenType.NUMBER, 156.0),
        ('variable', TokenType.IDENTIFIER, "variable"),
        ('', TokenType.EOF, None),
        ('// comment1 \n var', TokenType.VAR, None),
        (
            '// "string1" \n // "string2" \n "string3"',
            TokenType.STRING,
            "string3"
        )
    )
)
def test_comment_filter_get_next_token(
    text: str,
    token_type: TokenType,
    value: int | float | str | None
):
    lexer = create_lexer(text)
    filter = LexerWithoutComments(lexer)

    token = filter.next_token()

    assert token is not None
    assert token.type == token_type
    assert token.value == value


TEST_TEXT_TOKENS_MAP = [
    (
        "var a = 5;  \n"
        "const b = a / 10;",
        [
            Token(TokenType.VAR, None, Position(1, 1, 0)),
            Token(TokenType.IDENTIFIER, "a", Position(1, 5, 4)),
            Token(TokenType.EQUAL, None, Position(1, 7, 6)),
            Token(TokenType.NUMBER, 5, Position(1, 9, 8)),
            Token(TokenType.SEMICOLON, None, Position(1, 10, 9)),
            Token(TokenType.CONST, None, Position(2, 1, 13)),
            Token(TokenType.IDENTIFIER, "b", Position(2, 7, 19)),
            Token(TokenType.EQUAL, None, Position(2, 9, 21)),
            Token(TokenType.IDENTIFIER, "a", Position(2, 11, 23)),
            Token(TokenType.SLASH, None, Position(2, 13, 25)),
            Token(TokenType.NUMBER, 10, Position(2, 15, 27)),
            Token(TokenType.SEMICOLON, None, Position(2, 17, 29)),
            Token(TokenType.EOF, None, Position(2, 18, 30))
        ],
    ),
    (
        'match ("John") {\n'
        '   (Str as name) if someFunction(name): print("Hello" + name);\n'
        '   (_): print("Hello!");\n'
        '}',
        [
            Token(TokenType.MATCH, None, Position(1, 1, 0)),
            Token(TokenType.LEFT_PAREN, None, Position(1, 7, 6)),
            Token(TokenType.STRING, "John", Position(1, 8, 7)),
            Token(TokenType.RIGHT_PAREN, None, Position(1, 14, 13)),
            Token(TokenType.LEFT_BRACE, None, Position(1, 16, 15)),
            Token(TokenType.LEFT_PAREN, None, Position(2, 4, 20)),
            Token(TokenType.STRING_TYPE, None, Position(2, 5, 21)),
            Token(TokenType.AS, None, Position(2, 9, 25)),
            Token(TokenType.IDENTIFIER, "name", Position(2, 12, 28)),
            Token(TokenType.RIGHT_PAREN, None, Position(2, 16, 32)),
            Token(TokenType.IF, None, Position(2, 18, 34)),
            Token(TokenType.IDENTIFIER, "someFunction", Position(2, 21, 37)),
            Token(TokenType.LEFT_PAREN, None, Position(2, 33, 49)),
            Token(TokenType.IDENTIFIER, "name", Position(2, 34, 50)),
            Token(TokenType.RIGHT_PAREN, None, Position(2, 38, 54)),
            Token(TokenType.COLON, None, Position(2, 39, 55)),
            Token(TokenType.IDENTIFIER, "print", Position(2, 41, 57)),
            Token(TokenType.LEFT_PAREN, None, Position(2, 46, 62)),
            Token(TokenType.STRING, "Hello", Position(2, 47, 63)),
            Token(TokenType.PLUS, None, Position(2, 55, 71)),
            Token(TokenType.IDENTIFIER, "name", Position(2, 57, 73)),
            Token(TokenType.RIGHT_PAREN, None, Position(2, 61, 77)),
            Token(TokenType.SEMICOLON, None, Position(2, 62, 78)),
            Token(TokenType.LEFT_PAREN, None, Position(3, 4, 83)),
            Token(TokenType.UNDERSCORE, None, Position(3, 5, 84)),
            Token(TokenType.RIGHT_PAREN, None, Position(3, 6, 85)),
            Token(TokenType.COLON, None, Position(3, 7, 86)),
            Token(TokenType.IDENTIFIER, "print", Position(3, 9, 88)),
            Token(TokenType.LEFT_PAREN, None, Position(3, 14, 93)),
            Token(TokenType.STRING, "Hello!", Position(3, 15, 94)),
            Token(TokenType.RIGHT_PAREN, None, Position(3, 23, 102)),
            Token(TokenType.SEMICOLON, None, Position(3, 24, 103)),
            Token(TokenType.RIGHT_BRACE, None, Position(4, 1, 105)),
            Token(TokenType.EOF, None, Position(4, 2, 106)),
        ]
    )
]


@pytest.mark.parametrize("text, tokens", TEST_TEXT_TOKENS_MAP)
def test_lexer(text: str, tokens: list[Token]):
    stream = TextStream(text)
    lexer = Lexer(stream)

    assert get_all_tokens(lexer) == tokens
