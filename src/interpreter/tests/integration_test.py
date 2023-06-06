import io
import sys
import pytest

from lexer.streams import FileStream
from lexer.lexers import Lexer

from parser.parser import Parser

from interpreter.interpreter import Interpreter


def interpret(filename: str) -> str:
    with open(f"src/interpreter/tests/resources/{filename}", 'r') as f:
        stream = FileStream(f)
        lexer = Lexer(stream)
        parser = Parser(lexer)
        program = parser.parse()
        interpreter = Interpreter()
        captured_output = io.StringIO()
        sys.stdout = captured_output
        program.accept(interpreter)
        sys.stdout = sys.__stdout__
        return captured_output.getvalue()


FILENAME_EXPECTED_OUTPUT = (
    ("binary.txt", (
        3, 4, 1, 2, 7.3, 2, 0, 1, 10, 8, 9.5, "72a", 5, 10,
        "helloworld", "The answer is: 12", "The answer is: true",
        "Function name: print", 30, 30, 7, 2.5
    )),
    ("comparison.txt", (
        "true", "true", "true", "true", "true", "true", "true",
        "true", "true", "true", "false", "true", "true", "true",
        "true", "true", "true", "true", "true", "true", "true"
    )),
    ("variables.txt", (
        "string", "nil", 5, 6, 1, 1, "string"
    )),
    ("if.txt", (
        "Should sell", "Sold 30 stocks for 54$",
        "Money balance: 1288$", "Stock balance: 5"
    )),
    ("while.txt", (
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 8, 6, 4, 2, 0
    )),
    ("functions.txt", (
        3, 10, "nil",
        0, 1, 1, 2, 3, 5, 8, 13, 21, 34,
    )),
    ("pattern_matching.txt", (
        "Number", "Boolean", "Boolean", "String", "Function", "Nil",
        0, 1, "-100<-53<1", "66!=100", 100,
        "first", "second", "third", "fourth", "on Y", "on X",
        "Invalid coords: x, y",
    )),
)


@pytest.mark.parametrize(
    "filename, expected_output", FILENAME_EXPECTED_OUTPUT
)
def test_program(filename: str, expected_output: str):
    output = interpret(filename)
    expected_output = [str(x) for x in expected_output]
    assert output == "\n".join(expected_output) + "\n"
