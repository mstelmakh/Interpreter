from parser.models import (
    Program,
    BinaryExpr,
    Visitor,
    AssignmentExpr,
    LiteralExpr,
    UnaryExpr,
    LogicalExpr,
    GroupingExpr,
    IdentifierExpr,
    CallExpr,
    BlockStmt,
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
    Parameter
)


class AstPrinter(Visitor):
    def __init__(self):
        self.spaces = 0

    def print_type_and_indent(func):
        def wrapper(self, obj):
            self._print_type(obj)
            self.spaces += 2
            result = func(self, obj)
            self.spaces -= 2
            return result
        return wrapper

    @print_type_and_indent
    def visit_program(self, program: Program) -> str:
        for statement in program.statements:
            statement.accept(self)

    @print_type_and_indent
    def visit_assignment_expr(self, expr: AssignmentExpr):
        self._print(str(expr.name))
        expr.value.accept(self)

    @print_type_and_indent
    def visit_binary(self, expr: BinaryExpr):
        expr.left.accept(self)
        self._print(str(expr.operator))
        expr.right.accept(self)

    @print_type_and_indent
    def visit_unary(self, expr: UnaryExpr):
        self._print(str(expr.operator))
        expr.right.accept(self)

    @print_type_and_indent
    def visit_logical(self, expr: LogicalExpr):
        expr.left.accept(self)
        self._print(str(expr.operator))
        expr.right.accept(self)

    @print_type_and_indent
    def visit_grouping(self, expr: GroupingExpr):
        expr.expression.accept(self)

    @print_type_and_indent
    def visit_call(self, expr: CallExpr):
        expr.calee.accept(self)
        self._print("Arguments")
        self.spaces += 2
        for argument in expr.arguments:
            argument.accept(self)
        self.spaces -= 2

    @print_type_and_indent
    def visit_block_stmt(self, stmt: BlockStmt):
        for statement in stmt.statements:
            statement.accept(self)

    @print_type_and_indent
    def visit_function_stmt(self, stmt: FunctionStmt):
        for param in stmt.params:
            param.accept(self)
        stmt.block.accept(self)

    @print_type_and_indent
    def visit_variable_stmt(self, stmt: VariableStmt):
        self._print(str(stmt.name))
        self._print("is_const=" + str(stmt.is_const))
        if stmt.expression:
            stmt.expression.accept(self)

    @print_type_and_indent
    def visit_if_stmt(self, stmt: IfStmt):
        stmt.condition.accept(self)
        stmt.body.accept(self)
        if stmt.body_else:
            stmt.body_else.accept(self)

    @print_type_and_indent
    def visit_while_stmt(self, stmt: WhileStmt):
        stmt.condition.accept(self)
        stmt.body.accept(self)

    @print_type_and_indent
    def visit_return_stmt(self, stmt: ReturnStmt):
        if stmt.expression:
            stmt.expression.accept(self)

    @print_type_and_indent
    def visit_match_stmt(self, stmt: MatchStmt):
        self._print(str(stmt.arguments))
        for case_block in stmt.case_blocks:
            case_block.accept(self)

    @print_type_and_indent
    def visit_case_stmt(self, stmt: CaseStmt):
        for pattern in stmt.patterns:
            pattern.accept(self)
        if stmt.guard:
            stmt.guard.accept(self)
        stmt.body.accept(self)

    @print_type_and_indent
    def visit_guard(self, stmt: Guard):
        stmt.condition.accept(self)

    @print_type_and_indent
    def visit_pattern_expr(self, stmt: PatternExpr):
        if stmt.pattern:
            stmt.pattern.accept(self)
        if stmt.name:
            self._print(str(stmt.name))

    @print_type_and_indent
    def visit_compare_pattern_expr(self, stmt: ComparePatternExpr):
        self._print(str(stmt.operator))
        stmt.right.accept(self)

    def visit_type_pattern_expr(self, stmt: TypePatternExpr):
        self._print(str(stmt))

    def visit_literal(self, expr: LiteralExpr):
        self._print(str(expr))

    def visit_identifier(self, expr: IdentifierExpr):
        self._print(str(expr))

    def visit_parameter(self, parameter: Parameter):
        self._print(str(parameter))

    def _print(self, string: str):
        print(" "*self.spaces + string)

    def _print_type(self, obj: any):
        self._print(type(obj).__name__)
