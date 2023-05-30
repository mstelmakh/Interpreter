import pytest

from interpreter.tests.utils import create_program

from interpreter.interpreter import Interpreter
from interpreter.exceptions import (
    UndefinedVariableError,
    UndefinedFunctionError,
    InvalidArgumentNumberError,
    NumberConversionError,
    DivisionByZeroError,
    ConstantRedefinitionError,
    RedefinitionError
)


@pytest.mark.parametrize(
    "text, expected_result", (
        # Addition
        ("1 + 2", 3), ("4 + 6", 10), ('"5" + 3', 8),
        ("0 + 000", 0), ("0 + 00001", 1), ("1.10000 + 0", 1.1),
        ('7 + "2.5"', 9.5), ('7 + "2a"', "72a"),
        ("true + true", 2), ("false + false", 0), ("true + false", 1),
        ('"function: " + print', "function: print"), ('1 + print', "1print"),
        ('print + 1', "print1"), ('print + print', "printprint"),
        ('"hello" + "world"', "helloworld"),
        ('"The answer is: " + 12', "The answer is: 12"),
        ('"The answer is: " + 12.5', "The answer is: 12.5"),
        ('"The answer is: " + true', "The answer is: true"),
        ('"The answer is: " + false', "The answer is: false"),
        ('"The answer is: " + nil', "The answer is: nil"),

        # Subtraction
        ('"15" * 2', 30), ('"15" * 2.5', 37.5), ('"15" * "2"', 30),
        ("1 - 2", -1), ("4 - 6", -2), ('"5" - 3', 2),
        ("0 - 000", 0), ("0 - 00001", -1), ("1.10000 - 0", 1.1),
        ('7 - "2.5"', 4.5), ("true - true", 0), ("false - false", 0),
        ("true - false", 1), ("true - nil", 1), ("false - nil", 0),

        # Multiplication
        ("1 * 2", 2), ("4 * 6", 24), ('"5" * 3', 15),
        ("0 * 000", 0), ("0 * 00001", 0), ("1.10000 * 0", 0),
        ('7 * "2.5"', 17.5), ("true * true", 1), ("false * false", 0),
        ("true * false", 0), ("true * nil", 0), ("false * nil", 0),

        # Division
        ("1 / 2", 0.5), ("4 / 6", 4/6), ('"5" / 3', 5/3),
        ("0 / 00001", 0), ('7 / "2.5"', 7/2.5), ("true / true", 1),
        ("nil / 0.00100", 0),

        # Comparison
        ("1 == 2", False), ("4 == 6", False), ('"5" == 3', False),
        ("0 == 000", True), ("0 == 00001", False), ("1.10000 == 0", False),
        ('5 == "5"', True), ('5 == "5.0"', True), ('5 == "5.000000"', True),
        ('1 == true', True), ('0 == false', True), ('0 == nil', True),
        ('7 == "2.5"', False), ("true == true", True),
        ("false == false", True), ("true == false", False),
        ("true == nil", False), ("false == nil", True),
        ('print == "print"', True), ('print == print', True),

        ("1 != 2", True), ("4 != 6", True), ('"5" != 3', True),
        ("0 != 000", False), ("1 != 00001", False), ("1.10000 != 1.1", False),
        ('5 != "5"', False), ('5 != "5.0"', False), ('5 != "5.000000"', False),
        ('1 != true', False), ('0 != false', False), ('0 != nil', False),
        ('7 != "2.5"', True), ("true != true", False),
        ("false != false", False), ("true != false", True),
        ("true != nil", True), ("false != nil", False),
        ('print != "print"', False), ('print != print', False),

        ("1 < 2", True), ("4 < 6", True), ('"5" < 3', False),
        ("0 < 000", False), ("0 < 00001", True), ("1.10000 < 0", False),
        ('5 < "5"', False), ('5 < "5.0"', False), ('5 < "5.000000"', False),
        ('1 < true', False), ('0 < false', False), ('0 < nil', False),
        ('7 < "2.5"', False), ("true < true", False),
        ("false < false", False), ("true < false", False),
        ("true < nil", False), ("false < nil", False),
        ('print < "print"', False), ('print < print', False),

        ("1 <= 2", True), ("4 <= 6", True), ('"5" <= 3', False),
        ("0 <= 000", True), ("0 <= 00001", True), ("1.10000 <= 0", False),
        ('5 <= "5"', True), ('5 <= "5.0"', True), ('5 <= "5.000000"', True),
        ('1 <= true', True), ('0 <= false', True), ('0 <= nil', True),
        ('7 <= "2.5"', False), ("true <= true", True),
        ("false <= false", True), ("true <= false", False),
        ("true <= nil", False), ("false <= nil", True),
        ('print <= "print"', True), ('print <= print', True),

        ("1 > 2", False), ("4 > 6", False), ('"5" > 3', True),
        ("0 > 000", False), ("0 > 00001", False), ("1.10000 > 0", True),
        ('5 > "5"', False), ('5 > "5.0"', False), ('5 > "5.000000"', False),
        ('1 > true', False), ('0 > false', False), ('0 > nil', False),
        ('7 > "2.5"', True), ("true > true", False),
        ("false > false", False), ("true > false", True),
        ("true > nil", True), ("false > nil", False),
        ('print > "print"', False), ('print > print', False),

        ("1 >= 2", False), ("4 >= 6", False), ('"5" >= 3', True),
        ("0 >= 000", True), ("0 >= 00001", False), ("1.10000 >= 0", True),
        ('5 >= "5"', True), ('5 >= "5.0"', True), ('5 >= "5.000000"', True),
        ('1 >= true', True), ('0 >= false', True), ('0 >= nil', True),
        ('7 >= "2.5"', True), ("true >= true", True),
        ("false >= false", True), ("true >= false", True),
        ("true >= nil", True), ("false >= nil", True),
        ('print >= "print"', True), ('print >= print', True),
    )
)
def test_binary(text, expected_result):
    program = create_program(text + ";")
    interpreter = Interpreter()
    result = program.statements[0].accept(interpreter)
    assert result == expected_result


@pytest.mark.parametrize(
    "text, expected_error", (
        # Addition
        ("1 + a", UndefinedVariableError),
        ("a + 1", UndefinedVariableError),

        # Subtraction
        ("1 - a", UndefinedVariableError),
        ("a - 1", UndefinedVariableError),
        ('"2a" - 1', NumberConversionError),
        ('1 - "2a"', NumberConversionError),

        # Multiplication
        ("1 * a", UndefinedVariableError),
        ("a * 1", UndefinedVariableError),
        ('"2a" * 1', NumberConversionError),
        ('1 * "2a"', NumberConversionError),

        # Division
        ("1 / a", UndefinedVariableError),
        ("a / 1", UndefinedVariableError),
        ('"2a" / 1', NumberConversionError),
        ('1 / "2a"', NumberConversionError),
        ("1 / 0", DivisionByZeroError),
        ("1 / 0.0", DivisionByZeroError),
        ("1 / nil", DivisionByZeroError),
        ("nil / 0", DivisionByZeroError),
        ("1.1 / false", DivisionByZeroError),
        ("true / 0.0", DivisionByZeroError),

        # Comparison
        ("1 == a", UndefinedVariableError),
        ("a == 1", UndefinedVariableError),
        ("1 != a", UndefinedVariableError),
        ("a != 1", UndefinedVariableError),
        ("1 < a", UndefinedVariableError),
        ("a < 1", UndefinedVariableError),
        ("1 <= a", UndefinedVariableError),
        ("a <= 1", UndefinedVariableError),
        ("1 > a", UndefinedVariableError),
        ("a > 1", UndefinedVariableError),
        ("1 >= a", UndefinedVariableError),
        ("a >= 1", UndefinedVariableError),
    )
)
def test_binary_error(text, expected_error):
    program = create_program(text + ";")
    interpreter = Interpreter()
    with pytest.raises(expected_error):
        program.statements[0].accept(interpreter)


@pytest.mark.parametrize(
    "text, expected_result", (
        ("not true", False), ("not false", True), ("not nil", True),
        ("not 1", False), ("not 0", True), ("not 0.0", True),
        ('not "1"', False), ('not ""', True), ('not "0"', False),
        ("-1", -1), ("-0", 0), ("-0.0", 0), ('-"1"', -1), ('-"0"', 0),
        ('-"0.0"', 0),
    )
)
def test_unary(text, expected_result):
    program = create_program(text + ";")
    interpreter = Interpreter()
    result = program.statements[0].accept(interpreter)
    assert result == expected_result


@pytest.mark.parametrize(
    "text, expected_error", (
        ("not a", UndefinedVariableError),
        ("-a", UndefinedVariableError),
        ('-"a"', NumberConversionError),
    )
)
def test_unary_error(text, expected_error):
    program = create_program(text + ";")
    interpreter = Interpreter()
    with pytest.raises(expected_error):
        program.statements[0].accept(interpreter)


@pytest.mark.parametrize(
    "text, expected_result", (
        ("true and true", True), ("true and false", False),
        ("false and true", False), ("false and false", False),
        ("true and nil", None), ("false and nil", False),
        ("nil and true", None), ("nil and false", None),
        ("nil and nil", None), ("true and 1", 1), ("false and 1", False),
        ("1 and true", True), ("1 and false", False), ("1 and nil", None),
        ("1 and 0", 0), ("0 and 1", 0), ("0 and 0", 0), ("0 and nil", 0),
        ("1 and 1.0", 1.0), ("1.0 and 1", 1.0), ("1.0 and 1.0", 1.0),
    )
)
def test_logical(text, expected_result):
    program = create_program(text + ";")
    interpreter = Interpreter()
    result = program.statements[0].accept(interpreter)
    assert result == expected_result


def test_grouping():
    pass


def test_get_variable():
    pass


def test_get_variable_error():
    pass


def test_define_variable():
    pass


def test_define_variable_error():
    pass


def test_assign_variable():
    pass


def test_assign_variable_error():
    pass


def test_function_call():
    pass


def test_function_call_error():
    pass


def test_function_declaration():
    pass


def test_function_declaration_error():
    pass
