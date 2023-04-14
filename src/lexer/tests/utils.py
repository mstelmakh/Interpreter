from lexer.lexers import Lexer
from lexer.tokens import Token, TokenType, SINGLE_CHAR_MAP, COMPOSITE_CHAR_MAP
from lexer.streams import TextStream


def get_all_tokens(lexer: Lexer) -> Token:
    result = []
    token = lexer.next_token()
    while True:
        if token:
            result.append(token)
        if token and token.type == TokenType.EOF:
            break
        token = lexer.next_token()
    return result


def create_lexer(text: str) -> Lexer:
    stream = TextStream(text)
    return Lexer(stream)


def get_single_char_operators_beginning_of_composite(
) -> list[tuple[str, TokenType]]:
    """Returns all the single char operators that
    are also a beginning of a composite char operators."""
    result = []
    for composite in COMPOSITE_CHAR_MAP.keys():
        if composite[0] in SINGLE_CHAR_MAP:
            result.append((composite[0], SINGLE_CHAR_MAP[composite[0]]))
            continue
    return result
