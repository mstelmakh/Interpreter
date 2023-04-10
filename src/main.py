from sys import argv

from lexer.streams import FileStream, TextStream
from lexer.lexers import Lexer, LexerWithoutComments
from lexer.tokens import TokenType
from error_handlers import ErrorHandler


def run_prompt() -> None:
    while True:
        text = input("> ")
        text_iterator = iter(text)
        stream = TextStream(text_iterator)
        error_handler = ErrorHandler()
        lexer = Lexer(stream, error_handler)
        filter = LexerWithoutComments(lexer)
        token = filter.next_token()
        while (token and not token.type == TokenType.EOF) or not token:
            print(token)
            token = lexer.next_token()


def run(path: str) -> None:
    with open(path, 'r') as f:
        stream = FileStream(f)
        error_handler = ErrorHandler()
        lexer = Lexer(stream, error_handler)
        lexer = LexerWithoutComments(lexer)
        token = lexer.next_token()
        while (token and not token.type == TokenType.EOF) or not token:
            print(token)
            token = lexer.next_token()


if __name__ == "__main__":
    if (len(argv) == 2):
        run(argv[1])
    elif (len(argv) == 1):
        run_prompt()
    else:
        print("Usage: python main.py [script]")
        exit()
