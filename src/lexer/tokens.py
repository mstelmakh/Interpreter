from enum import Enum, auto
from dataclasses import dataclass

from lexer.streams import Position


class TokenType(Enum):
    # Single-character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()

    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    COLON = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    # One or two character tokens.
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    COMMENT = auto()

    # Literals.
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords.
    IF = auto()
    ELSE = auto()

    AND = auto()
    OR = auto()
    NOT = auto()

    FALSE = auto()
    TRUE = auto()

    FUNCTION = auto()
    RETURN = auto()

    WHILE = auto()

    NIL = auto()
    VAR = auto()
    CONST = auto()

    MATCH = auto()
    AS = auto()

    STRING_TYPE = auto()
    NUMBER_TYPE = auto()
    BOOL_TYPE = auto()
    FUNCTION_TYPE = auto()
    NIL_TYPE = auto()

    EOF = auto()


KEYWORDS_MAP = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,

    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,

    "false": TokenType.FALSE,
    "true": TokenType.TRUE,

    "fn": TokenType.FUNCTION,
    "return": TokenType.RETURN,

    "while": TokenType.WHILE,

    "nil": TokenType.NIL,
    "var": TokenType.VAR,
    "const": TokenType.CONST,

    "match": TokenType.MATCH,
    "as": TokenType.AS,

    "Str": TokenType.STRING_TYPE,
    "Num": TokenType.NUMBER_TYPE,
    "Bool": TokenType.BOOL_TYPE,
    "Func": TokenType.FUNCTION_TYPE,
    "Nil": TokenType.NIL_TYPE
}

SINGLE_CHAR_MAP = {
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    "-": TokenType.MINUS,
    "+": TokenType.PLUS,
    ":": TokenType.COLON,
    ";": TokenType.SEMICOLON,
    "*": TokenType.STAR,
    "=": TokenType.EQUAL,
    "<": TokenType.LESS,
    ">": TokenType.GREATER,
    "/": TokenType.SLASH,
}

COMMENT_CHAR = "//"

INDENTATION_CHARS = [" ", "\r", "\t", "\n"]

COMPOSITE_CHAR_MAP = {
    "!=": TokenType.BANG_EQUAL,
    "==": TokenType.EQUAL_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    ">=": TokenType.GREATER_EQUAL
}


@dataclass
class Token:
    type: TokenType
    value: int | float | str | None
    position: Position
