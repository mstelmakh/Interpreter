import pytest

from lexer.tests.utils import create_lexer

from parser.parser import Parser
from parser.exceptions import ParserError


def create_parser(text: str) -> Parser:
    lexer = create_lexer(text)
    return Parser(lexer)


@pytest.mark.xfail(strict=True, reason="Utility function")
def test_text_raises_error(text: str, error: type[ParserError]):
    parser = create_parser(text)
    with pytest.raises(error):
        parser.parse()
