import pytest

from lexer.tests.utils import create_lexer
from lexer.tokens import TokenType

from parser.parser import Parser
from parser.tests.utils import create_parser

from parser.models import (
    Program,
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
    InvalidSyntaxError,
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
    ("fn sum(a, b)", MissingFunctionBodyError),
    ("fn sum(a, b) ;", MissingFunctionBodyError),

))
def test_function_declaration_error(text: str, error: type[ParserError]):
    parser = create_parser(text)
    with pytest.raises(error):
        parser.parse()


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
    assert variable.name == name
    assert variable.expression == expression
    assert variable.is_const == is_const


@pytest.mark.parametrize("text, error", (
    ("var = 2;", MissingVariableNameError),
    ("var a = ;", MissingExpressionError),
    ("var a = 2", MissingSemicolonError),
))
def test_variable_declaration_error(text: str, error: type[ParserError]):
    parser = create_parser(text)
    with pytest.raises(error):
        parser.parse()


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
    assert if_stmt.condition == condition
    assert if_stmt.body == body
    assert if_stmt.body_else == body_else


@pytest.mark.parametrize("text, error", (
    ("if true) {return true;}", MissingLeftParenthesisError),
    ("if () {return true;}", MissingIfConditionError),
    ("if (true {return true;}", MissingRightParenthesisError),
    ("if (true);", MissingIfBodyError),
    ("if (true)", MissingIfBodyError),
    ("if (true) {return true;} else;", MissingElseBodyError),
    ("if (true) {return true;} else", MissingElseBodyError),
))
def test_if_error(text: str, error: type[ParserError]):
    parser = create_parser(text)
    with pytest.raises(error):
        parser.parse()


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
    assert while_stmt.condition == condition
    assert while_stmt.body == body


@pytest.mark.parametrize("text, error", (
    ("while true) {i = i + 1;}", MissingLeftParenthesisError),
    ("while ()) {i = i + 1;}", MissingWhileConditionError),
    ("while (true {i = i + 1;}", MissingRightParenthesisError),
    ("while (true)", MissingWhileBodyError),
    ("while (true);", MissingWhileBodyError),
))
def test_while_error(text: str, error: type[ParserError]):
    parser = create_parser(text)
    with pytest.raises(error):
        parser.parse()


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
    assert return_stmt.expression == expression


@pytest.mark.parametrize("text, error", (
    ("return", MissingSemicolonError),
    ("return true", MissingSemicolonError),
    ("return a or b or c", MissingSemicolonError),
))
def test_return_error(text: str, error: type[ParserError]):
    parser = create_parser(text)
    with pytest.raises(error):
        parser.parse()


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
                PatternExpr(ComparePatternExpr(None, LiteralExpr(0)), None)],
                None,
                LiteralExpr("Nothing")),
            CaseStmt([
                PatternExpr(
                    ComparePatternExpr(
                        None,
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
                        ComparePatternExpr(None, LiteralExpr(0))
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
    parser = create_parser(text)
    with pytest.raises(error):
        parser.parse()
