import pytest

from interpreter.tests.utils import create_program, test_text_raises_error

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
    test_text_raises_error(text + ";", expected_error)


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
    test_text_raises_error(text + ";", expected_error)


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


@pytest.mark.parametrize(
    "initializer, expected_name, expected_value", (
        ("a = 1", "a", 1), ("a = 1.0", "a", 1.0), ('a = "1"', "a", "1"),
        ("a = true", "a", True), ("a = false", "a", False),
        ("a = nil", "a", None), ('a = "a"', "a", "a"), ('a = ""', "a", ""),
        ('someValue = "hello\\tworld"', "someValue", "hello\tworld"),
        ('var2 = "hello\\nworld"', "var2", "hello\nworld"),
        ('new_var = "hello\\rworld"', "new_var", "hello\rworld"),
        ('VAR = "hello\\\\world"', "VAR", "hello\\world"),
    )
)
def test_define_variable(initializer, expected_name, expected_value):
    text = f"var {initializer};"
    program = create_program(text)
    interpreter = Interpreter()
    program.accept(interpreter)
    assert interpreter.environment.get(expected_name) == expected_value


@pytest.mark.parametrize(
    "initializer, expected_name, expected_value", (
        ("a = 1", "a", 1), ("a = 1.0", "a", 1.0), ('a = "1"', "a", "1"),
        ("a = true", "a", True), ("a = false", "a", False),
        ("a = nil", "a", None), ('a = "a"', "a", "a"), ('a = ""', "a", ""),
        ('someValue = "hello\\tworld"', "someValue", "hello\tworld"),
        ('var2 = "hello\\nworld"', "var2", "hello\nworld"),
        ('new_var = "hello\\rworld"', "new_var", "hello\rworld"),
        ('VAR = "hello\\\\world"', "VAR", "hello\\world"),
        ('CONST = "hello\\\\world"', "CONST", "hello\\world"),
    )
)
def test_define_variable_const(initializer, expected_name, expected_value):
    text = f"const {initializer};"
    program = create_program(text)
    interpreter = Interpreter()
    program.accept(interpreter)
    assert interpreter.environment.get(expected_name) == expected_value


@pytest.mark.parametrize(
    "text, expected_error", (
        ("var a = 1; var a = 2;", RedefinitionError),
        ("var a = 1; const a = 2;", RedefinitionError),
        ("const a = 1; var a = 2;", RedefinitionError),
        ("const a = 1; a = 2;", ConstantRedefinitionError),
        ("const a = 1; fn a() {}", ConstantRedefinitionError),
    )
)
def test_define_variable_error(text, expected_error):
    test_text_raises_error(text, expected_error)


def test_get_variable():
    text = "var a = 1; a;"
    program = create_program(text)
    interpreter = Interpreter()
    program.statements[0].accept(interpreter)
    result = program.statements[1].accept(interpreter)
    assert result == 1


def test_get_variable_error():
    test_text_raises_error("a;", UndefinedVariableError)


@pytest.mark.parametrize(
    "text, name, expected_value", (
        ("a = 2;", "a", 2), ("a = 2.0;", "a", 2.0),
        ("a = true;", "a", True), ("a = false;", "a", False),
        ("a = nil;", "a", None), ('a = "a";', "a", "a"),
        ('a = "";', "a", ""), ('a = "hello\\tworld";', "a", "hello\tworld"),
        ('someVar = 2 + 2;', "someVar", 4),
        ('result = nil or false or 2;', "result", 2),
    )
)
def test_assign_variable(text, name, expected_value):
    text = f"var {name}; " + text
    program = create_program(text)
    interpreter = Interpreter()
    program.accept(interpreter)
    assert interpreter.environment.get(name) == expected_value


@pytest.mark.parametrize(
    "text, expected_error", (
        ("a = 2;", UndefinedVariableError),
        ("const a = 2; a = 3;", ConstantRedefinitionError),
    )
)
def test_assign_variable_error(text, expected_error):
    test_text_raises_error(text, expected_error)


@pytest.mark.parametrize(
    "text, expected_result", (
        ((
            "fn add(a, b) {"
            "  return a + b;"
            "}"
            "add(1, 2);"
        ), 3),
        ((
            "fn nested(const a, b) {"
            "  fn inner(const c, d) {"
            "    return a + b + c + d;"
            "  }"
            "  return inner;"
            "}"
            "nested(1, 2)(3, 4);"
        ), 10),
    )
)
def test_function(text, expected_result):
    program = create_program(text)
    interpreter = Interpreter()
    program.statements[0].accept(interpreter)
    result = program.statements[1].accept(interpreter)
    assert result == expected_result


@pytest.mark.parametrize(
    "text, expected_error", (
        ((
            "fn immutable(const arg) {"
            "  arg = 2;"
            "}"
            "immutable(1);"
        ), ConstantRedefinitionError),
        ((
            "fn add(a, b) {"
            "  return a + b;"
            "}"
            "add(1);"
        ), InvalidArgumentNumberError),
        ("var undef_function = 1; undef_function();", UndefinedFunctionError),
    )
)
def test_function_error(text, expected_error):
    test_text_raises_error(text, expected_error)
