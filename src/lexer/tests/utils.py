from lexer.scanner import Scanner
from lexer.tokens import TokenType
from lexer.exceptions import LexerError
from error_handlers import BaseErrorHandler


class DebugErrorHandler(BaseErrorHandler):
    def __init__(self) -> None:
        self.errors: list[LexerError] = []

    def handle_lexer_error(self, exception: LexerError):
        self.errors.append(exception)


def get_all_tokens(scanner: Scanner):
    result = []
    token = scanner.next_token()
    while True:
        if token:
            result.append(token)
        if token and token.type == TokenType.EOF:
            break
        token = scanner.next_token()
    return result
