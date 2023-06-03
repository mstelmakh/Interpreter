from sys import argv

from lexer.streams import FileStream, TextStream, Stream
from lexer.lexers import Lexer  # , LexerWithoutComments
from lexer.exceptions import LexerError

from parser.parser import Parser
from parser.exceptions import ParserError

from interpreter.interpreter import Interpreter
from interpreter.exceptions import RuntimeError

from error_handlers import ErrorHandler


def run_prompt() -> None:
    while True:
        text = input("> ")
        stream = TextStream(text)
        run(stream)


def run_file(path: str) -> None:
    with open(path, 'r') as f:
        stream = FileStream(f)
        run(stream)


def run(stream: Stream) -> None:
    error_handler = ErrorHandler()
    try:
        lexer = Lexer(stream)
        # lexer = LexerWithoutComments(lexer)
        parser = Parser(lexer)
        program = parser.parse()
        # program.accept(AstPrinter())

        program.accept(Interpreter())
    except LexerError as e:
        error_handler.handle_lexer_error(e)
    except ParserError as e:
        error_handler.handle_parser_error(e)
    except RuntimeError as e:
        error_handler.handle_runtime_error(e)


if __name__ == "__main__":
    if (len(argv) == 2):
        run_file(argv[1])
    elif (len(argv) == 1):
        run_prompt()
    else:
        print("Usage: python main.py [script]")
        exit()
