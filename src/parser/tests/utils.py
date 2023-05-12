from lexer.tests.utils import create_lexer

from parser.parser import Parser


def create_parser(text: str) -> Parser:
    lexer = create_lexer(text)
    return Parser(lexer)
