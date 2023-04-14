import string

from lexer.utils import is_digit, is_alpha, is_alphanumeric


def test_is_digit_true():
    for i in range(10):
        assert is_digit(str(i)) is True


def test_is_digit_false():
    for i in ('num', '1e10', 'i', '^', '%', '+', '-1'):
        assert is_digit(i) is False


def test_is_alpha_true():
    for c in string.ascii_letters + '_':
        assert is_alpha(c) is True


def test_is_alpha_false():
    for c in range(10):
        assert is_alpha(str(c)) is False
    for c in ('!', '@', '$', '*', '+', '-', '='):
        assert is_alpha(str(c)) is False
    for c in ('ab', 'AB', 'A+', '"A*"'):
        assert is_alpha(str(c)) is False


def test_is_alphanumeric_true():
    for i in range(10):
        assert is_alphanumeric(str(i)) is True
    for c in string.ascii_letters + '_':
        assert is_alphanumeric(c) is True


def test_is_alphanumeric_false():
    for i in ('num', '1e10', '^', '%', '+', '-1'):
        assert is_alphanumeric(i) is False
    for c in ('!', '@', '$', '*', '+', '-', '='):
        assert is_alphanumeric(str(c)) is False
    for c in ('ab', 'AB', 'A+', '"A*"'):
        assert is_alphanumeric(str(c)) is False
