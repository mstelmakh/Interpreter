from parser.tests.utils import create_parser
from parser.models import Program


def create_program(text: str) -> Program:
    parser = create_parser(text)
    return parser.parse()
