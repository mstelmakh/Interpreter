import pytest

from parser.tests.utils import create_parser
from parser.models import Program
from interpreter.exceptions import RuntimeError
from interpreter.interpreter import Interpreter


def create_program(text: str) -> Program:
    parser = create_parser(text)
    return parser.parse()


@pytest.mark.xfail(strict=True, reason="Utility function")
def test_text_raises_error(text: str, error: type[RuntimeError]):
    program = create_program(text)
    interpreter = Interpreter()
    with pytest.raises(error):
        program.accept(interpreter)
