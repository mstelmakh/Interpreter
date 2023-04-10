from lexer.lexers import Lexer
from lexer.tokens import TokenType
from lexer.exceptions import LexerError
from lexer.streams import TextStream
from error_handlers import BaseErrorHandler


class DebugErrorHandler(BaseErrorHandler):
    def __init__(self) -> None:
        self.errors: list[LexerError] = []

    def handle_lexer_error(self, exception: LexerError):
        self.errors.append(exception)


def get_all_tokens(lexer: Lexer):
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
    error_handler = DebugErrorHandler()
    return Lexer(stream, error_handler)
