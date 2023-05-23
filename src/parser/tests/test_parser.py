import pytest

from lexer.tests.utils import create_lexer
from lexer.tokens import TokenType

from parser.parser import Parser
from parser.tests.utils import create_parser, test_text_raises_error

from parser.models import (
    Expr,
    AssignmentExpr,
    LogicalExpr,
    BinaryExpr,
    UnaryExpr,
    LiteralExpr,
    GroupingExpr,
    IdentifierExpr,
    CallExpr,
    Stmt,
    FunctionStmt,
    VariableStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    MatchStmt,
    CaseStmt,
    Guard,
    PatternExpr,
    ComparePatternExpr,
    TypePatternExpr,
    Parameter,
    BlockStmt
)
from parser.exceptions import (
    ParserError,
    MissingLeftParenthesisError,
    MissingRightParenthesisError,
    MissingLeftBraceError,
    MissingRightBraceError,
    MissingExpressionError,
    MissingPatternError,
    MissingMatchArgumentsError,
    MissingArgumentError,
    MissingIfConditionError,
    MissingWhileConditionError,
    MissingFunctionNameError,
    MissingFunctionBodyError,
    MissingIfBodyError,
    MissingElseBodyError,
    MissingWhileBodyError,
    MissingCaseBodyError,
    MissingVariableNameError,
    MissingSemicolonError,
    MissingColonError,
    MissingParameterError,
    MissingParameterNameError,
    MissingPatternIdentifierError,
    DuplicateParametersError,
    DuplicatePatternNamesError
)


def test_init_parser():
    text = "var a = 5;"
    lexer = create_lexer(text)
    parser = Parser(lexer)
    assert parser.current_token.type == TokenType.VAR


@pytest.mark.parametrize('text, expected_value', (
    ("0", 0), ("123456", 123456), ("00001", 1), ("00001.", 1.0),
    ("0.123", 0.123), ("0.00123", 0.00123), ("000.012300", 0.0123),
    ('"hello"', "hello"), ('"53+52"', "53+52"), ('"\nabc\t\n"', "\nabc\t\n"),
    ("true", True), ("false", False), ("nil", None)
))
def test_literal_success(
    text: str,
    expected_value: int | float | str | None
):
    parser = create_parser(text + ";")
    program = parser.parse()
    literal = program.statements[0]
    assert isinstance(literal, LiteralExpr)
    assert literal.value == expected_value


@pytest.mark.parametrize('text', (
    "variable", "orchid", "String", "andor", "whileas"
))
def test_identifier_success(
    text: str,
):
    parser = create_parser(text + ";")
    program = parser.parse()
    identifier = program.statements[0]
    assert isinstance(identifier, IdentifierExpr)
    assert identifier.name == text


@pytest.mark.parametrize('text, expression', (
    ("(variable)", IdentifierExpr("variable")),
    ('("string")', LiteralExpr("string")),
    ('(true)', LiteralExpr(True)),
    ('(2+5)', BinaryExpr(LiteralExpr(2), TokenType.PLUS, LiteralExpr(5))),
))
def test_grouping_success(
    text: str,
    expression: Expr
):
    parser = create_parser(text + ";")
    program = parser.parse()
    grouping = program.statements[0]
    assert isinstance(grouping, GroupingExpr)
    assert grouping.expression == expression


@pytest.mark.parametrize('text, error', (
    ("(2+5)", MissingSemicolonError),
    ("(2+5;", MissingRightParenthesisError),
))
def test_grouping_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, calee, arguments', (
    ('do_nothing()', IdentifierExpr("do_nothing"), []),
    ('print("hello")', IdentifierExpr("print"), [LiteralExpr("hello")]),
    (
        'is_true(true or false)',
        IdentifierExpr("is_true"),
        [LogicalExpr(LiteralExpr(True), TokenType.OR, LiteralExpr(False))]
    ),
    (
        'add(1)(2)',
        CallExpr(IdentifierExpr("add"), [LiteralExpr(1)]),
        [LiteralExpr(2)]
    ),
))
def test_call_success(
    text: str,
    calee: Expr,
    arguments: list[Expr]
):
    parser = create_parser(text + ";")
    program = parser.parse()
    call = program.statements[0]
    assert isinstance(call, CallExpr)
    assert call.calee == calee
    assert call.arguments == arguments


@pytest.mark.parametrize('text, error', (
    ('add(1)(2)', MissingSemicolonError),
    ('add(1(2);', MissingRightParenthesisError),
    ('add(1)(2;', MissingRightParenthesisError),
    ('add(1,)(2);', MissingArgumentError),
    ('add(1)(2,);', MissingArgumentError),
))
def test_call_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, operator, expression', (
    ("-2", TokenType.MINUS, LiteralExpr(2)),
    ("not true", TokenType.NOT, LiteralExpr(True)),
    (
        'not (2+"2">5)',
        TokenType.NOT,
        GroupingExpr(BinaryExpr(
            BinaryExpr(LiteralExpr(2), TokenType.PLUS, LiteralExpr("2")),
            TokenType.GREATER,
            LiteralExpr(5)
        ))
    ),
))
def test_unary_success(
    text: str,
    operator: TokenType,
    expression: Expr
):
    parser = create_parser(text + ";")
    program = parser.parse()
    unary = program.statements[0]
    assert isinstance(unary, UnaryExpr)
    assert unary.operator == operator
    assert unary.right == expression


@pytest.mark.parametrize('text, error', (
    ("-", MissingExpressionError),
    ("-;", MissingExpressionError),
    ("not", MissingExpressionError),
    ("not;", MissingExpressionError),
))
def test_unary_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, left, operator, right', (
    ('"a"*2', LiteralExpr("a"), TokenType.STAR, LiteralExpr(2)),
    ("-5/2", UnaryExpr(
        TokenType.MINUS, LiteralExpr(5)
        ),
     TokenType.SLASH, LiteralExpr(2)),
    ('7 + "2.5"', LiteralExpr(7), TokenType.PLUS, LiteralExpr("2.5")),
    ('10 - "foo"', LiteralExpr(10), TokenType.MINUS, LiteralExpr("foo")),
    ("1<=2", LiteralExpr(1), TokenType.LESS_EQUAL, LiteralExpr(2)),
    ('5<"5"', LiteralExpr(5), TokenType.LESS, LiteralExpr("5")),
    ('"5">10', LiteralExpr("5"), TokenType.GREATER, LiteralExpr(10)),
    ('"1000a">=1000',
     LiteralExpr("1000a"),
     TokenType.GREATER_EQUAL,
     LiteralExpr(1000)),
    ('123==123', LiteralExpr(123), TokenType.EQUAL_EQUAL, LiteralExpr(123)),
    ('"5"!=5', LiteralExpr("5"), TokenType.BANG_EQUAL, LiteralExpr(5)),
))
def test_binary_success(
    text: str,
    left: Expr,
    operator: TokenType,
    right: Expr
):
    parser = create_parser(text + ";")
    program = parser.parse()
    binary = program.statements[0]
    assert isinstance(binary, BinaryExpr)
    assert binary.left == left
    assert binary.operator == operator
    assert binary.right == right


@pytest.mark.parametrize('text', (
    '"7.5"*', '"string"/', "2+", '"7.5"-', '"greater">',
    '5<', '15>=', '15<=', '-5==', '00.100!='
))
def test_binary_error(text: str):
    test_text_raises_error(text, MissingExpressionError)


@pytest.mark.parametrize('text, left, operator, right', (
    ("true or false", LiteralExpr(True), TokenType.OR, LiteralExpr(False)),
    ("true and false", LiteralExpr(True), TokenType.AND, LiteralExpr(False)),
    (
        "(true and true) or (2 + 2 == 4)",
        GroupingExpr(
            LogicalExpr(LiteralExpr(True), TokenType.AND, LiteralExpr(True))
        ),
        TokenType.OR,
        GroupingExpr(
            BinaryExpr(
                BinaryExpr(LiteralExpr(2), TokenType.PLUS, LiteralExpr(2)),
                TokenType.EQUAL_EQUAL,
                LiteralExpr(4)
            )
        )
    ),
))
def test_logical_success(
    text: str,
    left: Expr,
    operator: TokenType,
    right: Expr
):
    parser = create_parser(text + ";")
    program = parser.parse()
    logical = program.statements[0]
    assert isinstance(logical, LogicalExpr)
    assert logical.left == left
    assert logical.operator == operator
    assert logical.right == right


@pytest.mark.parametrize('text, error', (
    ("true or", MissingExpressionError),
    ("true or;", MissingExpressionError),
    ("true and", MissingExpressionError),
    ("true and;", MissingExpressionError),
))
def test_logical_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, name, value', (
    ("x = 5", "x", LiteralExpr(5)),
    ('name = "John"', "name", LiteralExpr("John")),
    ('is_true = true and false',
     "is_true",
     LogicalExpr(LiteralExpr(True), TokenType.AND, LiteralExpr(False))),
    ('is_true = true or false and true',
     "is_true",
     LogicalExpr(
        LiteralExpr(True),
        TokenType.OR,
        LogicalExpr(LiteralExpr(False), TokenType.AND, LiteralExpr(True))
     )),
))
def test_assignment_success(
    text: str,
    name: str,
    value: Expr
):
    parser = create_parser(text + ";")
    program = parser.parse()
    assignment = program.statements[0]
    assert isinstance(assignment, AssignmentExpr)
    assert assignment.name == name
    assert assignment.value == value


@pytest.mark.parametrize('text, error', (
    ("x = 5", MissingSemicolonError),
    ("x = ", MissingExpressionError),
    ("x = ;", MissingExpressionError),
))
def test_assignment_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, name, expression, is_const', (
    ("var a = 5;", "a", LiteralExpr(5), False),
    ("const a = 5;", "a", LiteralExpr(5), True),
    ("var a;", "a", None, False),
    ("const a;", "a", None, True),
    ("var S = a*a;", "S",
     BinaryExpr(IdentifierExpr("a"), TokenType.STAR, IdentifierExpr("a")),
     False),
    ("const is_true = true or false;", "is_true",
     LogicalExpr(LiteralExpr(True), TokenType.OR, LiteralExpr(False)),
     True),
))
def test_variable_declaration_success(
    text: str,
    name: str,
    expression: Expr,
    is_const: bool
):
    parser = create_parser(text)
    program = parser.parse()
    variable = program.statements[0]
    assert isinstance(variable, VariableStmt)
    assert variable.name == name
    assert variable.expression == expression
    assert variable.is_const == is_const


@pytest.mark.parametrize("text, error", (
    ("var = 2;", MissingVariableNameError),
    ("var a = ;", MissingExpressionError),
    ("var a = 2", MissingSemicolonError),
))
def test_variable_declaration_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, name, params, block', (
    (
        "fn sum(a, b) {return a+b;}",
        "sum",
        [Parameter("a", False), Parameter("b", False)],
        BlockStmt([
            ReturnStmt(
                BinaryExpr(
                    IdentifierExpr("a"),
                    TokenType.PLUS,
                    IdentifierExpr("b")
                )
            )
        ])
    ),
    (
        "fn sum(const a, b) {return a+b;}",
        "sum",
        [Parameter("a", True), Parameter("b", False)],
        BlockStmt([
            ReturnStmt(
                BinaryExpr(
                    IdentifierExpr("a"),
                    TokenType.PLUS,
                    IdentifierExpr("b")
                )
            )
        ])
    ),
    (
        "fn four() {return 2+2;}",
        "four",
        [],
        BlockStmt([
            ReturnStmt(
                BinaryExpr(
                    LiteralExpr(2),
                    TokenType.PLUS,
                    LiteralExpr(2)
                )
            )
        ])
    ),
    (
        "fn nothing() {}",
        "nothing",
        [],
        BlockStmt([])
    ),
))
def test_function_declaration_success(
    text: str,
    name: str,
    params: list[Parameter],
    block: BlockStmt
):
    parser = create_parser(text)
    program = parser.parse()
    function = program.statements[0]
    assert isinstance(function, FunctionStmt)
    assert function.name == name
    assert function.params == params
    assert function.block == block


@pytest.mark.parametrize("text, error", (
    ("fn (a, b) {return a+b;}", MissingFunctionNameError),
    ("fn suma,b) {return a+b;}", MissingLeftParenthesisError),
    ("fn sum(a, b {return a+b;}", MissingRightParenthesisError),
    ("fn sum(a,) {return a+b;}", MissingParameterError),
    ("fn sum(a, const) {return a+b;}", MissingParameterNameError),
    ("fn sum(a, a) {return a+b;}", DuplicateParametersError),
    ("fn sum(a, b) {return a+b}", MissingSemicolonError),
    ("fn sum(a, b)", MissingFunctionBodyError),
    ("fn sum(a, b) ;", MissingFunctionBodyError),

))
def test_function_declaration_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, condition, body, body_else', (
    (
        "if (1>0) {return true;} else {return false;}",
        BinaryExpr(LiteralExpr(1), TokenType.GREATER, LiteralExpr(0)),
        BlockStmt([ReturnStmt(LiteralExpr(True))]),
        BlockStmt([ReturnStmt(LiteralExpr(False))])
    ),
    (
        "if (1>0) return true; else return false;",
        BinaryExpr(LiteralExpr(1), TokenType.GREATER, LiteralExpr(0)),
        ReturnStmt(LiteralExpr(True)),
        ReturnStmt(LiteralExpr(False))
    ),
    (
        (
            "if (true) {\n"
            "   var a = 4;\n"
            "   return a;\n"
            "}"
        ),
        LiteralExpr(True),
        BlockStmt([
            VariableStmt("a", LiteralExpr(4), False),
            ReturnStmt(IdentifierExpr("a"))
        ]),
        None
    ),
))
def test_if_success(
    text: str,
    condition: Expr,
    body: Stmt,
    body_else: Stmt | None
):
    parser = create_parser(text)
    program = parser.parse()
    if_stmt = program.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert if_stmt.condition == condition
    assert if_stmt.body == body
    assert if_stmt.body_else == body_else


@pytest.mark.parametrize("text, error", (
    ("if true) {return true;}", MissingLeftParenthesisError),
    ("if () {return true;}", MissingIfConditionError),
    ("if (true {return true;}", MissingRightParenthesisError),
    ("if (true) {return true}", MissingSemicolonError),
    ("if (true);", MissingIfBodyError),
    ("if (true)", MissingIfBodyError),
    ("if (true) {return true;} else;", MissingElseBodyError),
    ("if (true) {return true;} else", MissingElseBodyError),
))
def test_if_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, condition, body', (
    (
        "while (true) {i = i + 1;}",
        LiteralExpr(True),
        BlockStmt([AssignmentExpr(
            "i",
            BinaryExpr(IdentifierExpr("i"), TokenType.PLUS, LiteralExpr(1))
        )])
    ),
    (
        "while (true) i = i + 1;",
        LiteralExpr(True),
        AssignmentExpr(
            "i",
            BinaryExpr(IdentifierExpr("i"), TokenType.PLUS, LiteralExpr(1))
        )
    ),
    (
        "while (true) {if (i > 2) return true;}",
        LiteralExpr(True),
        BlockStmt([IfStmt(
            BinaryExpr(IdentifierExpr("i"), TokenType.GREATER, LiteralExpr(2)),
            ReturnStmt(LiteralExpr(True)),
            None
        )])
    ),
))
def test_while_success(
    text: str,
    condition: Expr,
    body: Stmt
):
    parser = create_parser(text)
    program = parser.parse()
    while_stmt = program.statements[0]
    assert isinstance(while_stmt, WhileStmt)
    assert while_stmt.condition == condition
    assert while_stmt.body == body


@pytest.mark.parametrize("text, error", (
    ("while true) {i = i + 1;}", MissingLeftParenthesisError),
    ("while ()) {i = i + 1;}", MissingWhileConditionError),
    ("while (true {i = i + 1;}", MissingRightParenthesisError),
    ("while (true) {i = i + 1}", MissingSemicolonError),
    ("while (true)", MissingWhileBodyError),
    ("while (true);", MissingWhileBodyError),
))
def test_while_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, expression', (
    ("return;", None),
    ("return true;", LiteralExpr(True)),
    (
        "return a or b or c;",
        LogicalExpr(
            LogicalExpr(
                IdentifierExpr("a"), TokenType.OR, IdentifierExpr("b")
            ),
            TokenType.OR,
            IdentifierExpr("c")
        )
    ),
))
def test_return_success(
    text: str,
    expression: Expr | None
):
    parser = create_parser(text)
    program = parser.parse()
    return_stmt = program.statements[0]
    assert isinstance(return_stmt, ReturnStmt)
    assert return_stmt.expression == expression


@pytest.mark.parametrize("text, error", (
    ("return", MissingSemicolonError),
    ("return true", MissingSemicolonError),
    ("return a or b or c", MissingSemicolonError),
))
def test_return_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)


@pytest.mark.parametrize('text, arguments, case_blocks', (
    (
        ('match (number) {\n'
         '    (0): "Nothing";\n'
         '    (-1): "One less than nothing";\n'
         '    (_): "Unknown";\n'
         '}'),
        [IdentifierExpr("number")],
        [
            CaseStmt([
                PatternExpr(ComparePatternExpr(
                    TokenType.EQUAL_EQUAL, LiteralExpr(0)), None
                )],
                None,
                LiteralExpr("Nothing")),
            CaseStmt([
                PatternExpr(
                    ComparePatternExpr(
                        TokenType.EQUAL_EQUAL,
                        UnaryExpr(TokenType.MINUS, LiteralExpr(1))
                    ),
                    None)],
                None,
                LiteralExpr("One less than nothing")),
            CaseStmt([
                PatternExpr(None, None)],
                None,
                LiteralExpr("Unknown")),
        ]
    ),
    (
        ('match ("John") {\n'
         '   (Str as name) if (someFunction(name)): "Hello1";\n'
         '   (_): "Hello2";\n'
         '}'),
        [LiteralExpr("John")],
        [
            CaseStmt([
                PatternExpr(TypePatternExpr(TokenType.STRING_TYPE), "name")],
                Guard(CallExpr(
                    IdentifierExpr("someFunction"),
                    [IdentifierExpr("name")]
                )),
                LiteralExpr("Hello1")),
            CaseStmt([
                PatternExpr(None, None)],
                None,
                LiteralExpr("Hello2")),
        ]
    ),
    (
        ('match (x, y) {\n'
         '   (Num and >0, Num and >0 ): "first";\n'
         '   (Num and 0, Num): "on Y";\n'
         '   (Num, Num): "on X";\n'
         '   (_ as x, _ as y): "Invalid coords";\n'
         '}'),
        [IdentifierExpr("x"), IdentifierExpr("y")],
        [
            CaseStmt([
                PatternExpr(
                    LogicalExpr(
                        TypePatternExpr(TokenType.NUMBER_TYPE),
                        TokenType.AND,
                        ComparePatternExpr(TokenType.GREATER, LiteralExpr(0))
                    ), None
                ),
                PatternExpr(
                    LogicalExpr(
                        TypePatternExpr(TokenType.NUMBER_TYPE),
                        TokenType.AND,
                        ComparePatternExpr(TokenType.GREATER, LiteralExpr(0))
                    ), None
                )
            ],
                None,
                LiteralExpr("first")
            ),
            CaseStmt([
                PatternExpr(
                    LogicalExpr(
                        TypePatternExpr(TokenType.NUMBER_TYPE),
                        TokenType.AND,
                        ComparePatternExpr(
                            TokenType.EQUAL_EQUAL, LiteralExpr(0)
                        )
                    ), None
                ),
                PatternExpr(TypePatternExpr(TokenType.NUMBER_TYPE), None)
            ],
                None,
                LiteralExpr("on Y")
            ),
            CaseStmt([
                PatternExpr(TypePatternExpr(TokenType.NUMBER_TYPE), None),
                PatternExpr(TypePatternExpr(TokenType.NUMBER_TYPE), None)
            ],
                None,
                LiteralExpr("on X")
            ),
            CaseStmt([
                PatternExpr(None, "x"),
                PatternExpr(None, "y")
            ],
                None,
                LiteralExpr("Invalid coords")
            ),
        ]
    ),
))
def test_match_success(
    text: str,
    arguments: list[Expr],
    case_blocks: list[CaseStmt]
):
    parser = create_parser(text)
    program = parser.parse()
    match_stmt = program.statements[0]
    assert isinstance(match_stmt, MatchStmt)
    assert match_stmt.arguments == arguments
    assert match_stmt.case_blocks == case_blocks


@pytest.mark.parametrize("text, error", (
    ('match a) {(_ as x): "x: " + x;}', MissingLeftParenthesisError),
    ('match () {(_ as x): "x: " + x;}', MissingMatchArgumentsError),
    ('match (a {(_ as x): "x: " + x;}', MissingRightParenthesisError),
    ('match (a,) {(_ as x): "x: " + x;}', MissingArgumentError),

    ('match (a) {(_ as x) if x>2): "x: " + x;}', MissingLeftParenthesisError),
    ('match (a) {(_ as x) if ()): "x: " + x;}', MissingIfConditionError),
    ('match (a) {(_ as x) if (x>2: "x: " + x;}', MissingRightParenthesisError),

    ('match (a) (_ as x): "x: " + x;}', MissingLeftBraceError),
    ('match (a) {(_ as x): "x: " + x;', MissingRightBraceError),

    ('match (a) {(): "x: " + x;}', MissingExpressionError),
    ('match (a) {(_ as x: "x: " + x;}', MissingRightParenthesisError),
    ('match (a) {(_ as x) "x: " + x;}', MissingColonError),
    ('match (a) {(_ as x): "x: " + x}', MissingSemicolonError),
    ('match (a) {(_ as x):}', MissingCaseBodyError),
    ('match (a) {(_ as x): ;}', MissingCaseBodyError),

    ('match (a) {(_ as x,): "x: " + x;}', MissingPatternError),
    ('match (a) {(_ as x, _ as x): "x: " + x;}', DuplicatePatternNamesError),
    ('match (a) {(_ as ): "x: " + x;}', MissingPatternIdentifierError),
    ('match (a) {(2 or as x): "x: " + x;}', MissingExpressionError),
    ('match (a) {(2 and as x): "x: " + x;}', MissingExpressionError),
    ('match (a) {(!= as x): "x: " + x;}', MissingExpressionError),
))
def test_match_error(text: str, error: type[ParserError]):
    test_text_raises_error(text, error)
