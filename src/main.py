from sys import argv

from lexer.streams import FileStream, TextStream, Stream
from lexer.lexers import Lexer  # , LexerWithoutComments

from parser.parser import Parser
# from parser.ast_printer import AstPrinter

from interpreter.interpreter import Interpreter


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
    lexer = Lexer(stream)
    # lexer = LexerWithoutComments(lexer)
    parser = Parser(lexer)
    program = parser.parse()
    # program.accept(AstPrinter())

    program.accept(Interpreter())


if __name__ == "__main__":
    if (len(argv) == 2):
        run_file(argv[1])
    elif (len(argv) == 1):
        run_prompt()
    else:
        print("Usage: python main.py [script]")
        exit()
