from lexer.tokens import TokenType

from parser.models import (
    Program,
    Expr,
    Stmt,
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

from interpreter.models import Environment, Callable, UserDefinedFunction
from interpreter.stdlib import PrintFunction
from interpreter.exceptions import (
    Return,
    NumberConversionError,
    UndefinedVariableError,
    UndefinedFunctionError,
    RedefinitionError,
    ConstantRedefinitionError,
    DivisionByZeroError,
    InvalidArgumentNumberError
)

Literal = int | float | str | bool | None


class Interpreter(Visitor):
    def __init__(self):
        self.environment = Environment()
        self.environment.define_function(PrintFunction())

    def visit_program(self, program: Program):
        for statement in program.statements:
            self.evaluate(statement)

    def visit_assignment_expr(self, expr: AssignmentExpr):
        value = self.evaluate(expr.value)
        try:
            self.environment.assign(expr.name, value)
            return value
        except (UndefinedVariableError, ConstantRedefinitionError) as e:
            raise e.__class__(expr.name, position=expr.position)

    def visit_binary(self, expr: BinaryExpr):
        match expr.operator:
            case TokenType.MINUS:
                return self._evaluate_binary_minus(expr.left, expr.right)
            case TokenType.PLUS:
                return self._evaluate_binary_plus(expr.left, expr.right)
            case TokenType.STAR:
                return self._evaluate_binary_multiply(expr.left, expr.right)
            case TokenType.SLASH:
                return self._evaluate_binary_divide(expr.left, expr.right)
            case (
                TokenType.GREATER_EQUAL
                | TokenType.GREATER
                | TokenType.LESS_EQUAL
                | TokenType.LESS
                | TokenType.EQUAL_EQUAL
                | TokenType.BANG_EQUAL
            ):
                return self._evaluate_binary_comparison(expr)

    def _evaluate_binary_minus(self, left_expr: Expr, right_expr: Expr):
        left = self.evaluate(left_expr)
        right = self.evaluate(right_expr)
        new_left = self.try_cast_to_number(left)
        new_right = self.try_cast_to_number(right)
        if new_left is not None and new_right is not None:
            return new_left - new_right
        raise NumberConversionError(
            left if new_left is None else right,
            left_expr.position if new_left is None else right_expr.position
        )

    def _evaluate_binary_plus(self, left_expr: Expr, right_expr: Expr):
        left = self.evaluate(left_expr)
        right = self.evaluate(right_expr)
        left, right = self._cast_binary_operands_to_common_type(left, right)
        return left + right

    def _cast_binary_operands_to_common_type(self, left, right):
        if (new_left := self.try_cast_to_number(left)) is not None:
            new_right = self.try_cast_to_number(right)
            if new_right is not None:
                return new_left, new_right
        if (new_right := self.try_cast_to_number(right)) is not None:
            new_left = self.try_cast_to_number(left)
            if new_left is not None:
                return new_left, new_right
        return self.cast_to_str(left), self.cast_to_str(right)

    def _evaluate_binary_multiply(self, left_expr: Expr, right_expr: Expr):
        left = self.evaluate(left_expr)
        right = self.evaluate(right_expr)
        new_left = self.try_cast_to_number(left)
        new_right = self.try_cast_to_number(right)
        if new_left is not None and new_right is not None:
            return new_left * new_right
        raise NumberConversionError(
            left if new_left is None else right,
            left_expr.position if new_left is None else right_expr.position
        )

    def _evaluate_binary_divide(self, left_expr: Expr, right_expr: Expr):
        left = self.evaluate(left_expr)
        right = self.evaluate(right_expr)
        new_left = self.try_cast_to_number(left)
        new_right = self.try_cast_to_number(right)
        if new_left is not None and new_right is not None:
            if new_right == 0:
                raise DivisionByZeroError(right_expr.position)
            return new_left / new_right
        raise NumberConversionError(
            left if new_left is None else right,
            left_expr.position if new_left is None else right_expr.position
        )

    def _evaluate_binary_comparison(self, expr: BinaryExpr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        operator_type = expr.operator
        left, right = self._cast_binary_operands_to_common_type(
            left,
            right
        )
        if operator_type == TokenType.GREATER_EQUAL:
            return left >= right
        if operator_type == TokenType.GREATER:
            return left > right
        if operator_type == TokenType.LESS_EQUAL:
            return left <= right
        if operator_type == TokenType.LESS:
            return left < right
        if operator_type == TokenType.EQUAL_EQUAL:
            return left == right
        if operator_type == TokenType.BANG_EQUAL:
            return left != right

    def visit_literal(self, expr: LiteralExpr):
        return expr.value

    def visit_unary(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)
        match expr.operator:
            case TokenType.MINUS:
                new_right = self.try_cast_to_number(right)
                if new_right is not None:
                    return -new_right
                raise NumberConversionError(right, expr.position)
            case TokenType.NOT:
                return not self.is_truthy(right)
        return None

    def visit_logical(self, expr: LogicalExpr):
        left = self.evaluate(expr.left)
        if expr.operator == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    def visit_grouping(self, expr: GroupingExpr):
        return self.evaluate(expr.expression)

    def visit_identifier(self, expr: IdentifierExpr):
        try:
            return self.environment.get(expr.name)
        except UndefinedVariableError:
            raise UndefinedVariableError(expr.name, expr.position)

    def visit_call(self, expr: CallExpr):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, Callable):
            raise UndefinedFunctionError(callee, expr.position)
        if callee.arity is not None and len(arguments) != callee.arity:
            raise InvalidArgumentNumberError(
                callee.name,
                callee.arity,
                len(arguments),
                expr.position
            )
        return callee.call(self, arguments)

    def visit_block_stmt(self, stmt: BlockStmt):
        self.execute_block(stmt.statements, Environment(self.environment))

    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_function_stmt(self, stmt: FunctionStmt):
        function = UserDefinedFunction(stmt, self.environment)
        try:
            self.environment.define_function(function)
        except ConstantRedefinitionError:
            raise ConstantRedefinitionError(stmt.name, stmt.position)

    def visit_variable_stmt(self, stmt: VariableStmt):
        value = None
        if stmt.expression:
            value = self.evaluate(stmt.expression)
        try:
            self.environment.define(stmt.name, value, stmt.is_const)
        except RedefinitionError:
            raise RedefinitionError(stmt.name, stmt.position)

    def visit_if_stmt(self, stmt: IfStmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        elif stmt.body_else:
            self.execute(stmt.body_else)

    def visit_while_stmt(self, stmt: WhileStmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_return_stmt(self, stmt: ReturnStmt):
        value = None
        if stmt.expression is not None:
            value = self.evaluate(stmt.expression)
        raise Return(value)

    def visit_match_stmt(self, stmt: MatchStmt):
        arguments = [self.evaluate(arg) for arg in stmt.arguments]
        for case in stmt.case_blocks:
            if not len(case.patterns) == len(arguments):
                raise InvalidArgumentNumberError(
                    "case",
                    len(arguments),
                    len(case.patterns),
                    stmt.position
                )
            if (
                all([
                    self._evaluate_pattern(pattern.pattern, arg)
                    for pattern, arg in zip(case.patterns, arguments)
                ])
                and (case.guard is None or self.evaluate(case.guard))
            ):
                previous = self.environment
                environment = Environment(self.environment)
                for pattern, arg in zip(case.patterns, arguments):
                    if pattern.name is not None:
                        environment.define(pattern.name, arg)
                self.environment = environment
                self.execute(case.body)
                self.environment = previous
                break

    def _evaluate_pattern(self, pattern: Expr, value: Literal) -> bool:
        if isinstance(pattern, LogicalExpr):
            left = self._evaluate_pattern(pattern.left, value)
            if pattern.operator == TokenType.OR:
                if self.is_truthy(left):
                    return True
            else:
                if not self.is_truthy(left):
                    return False
            return self._evaluate_pattern(pattern.right, value)
        if not pattern:
            return True
        return self.evaluate(pattern)(value)

    def visit_case_stmt(self, stmt: CaseStmt):
        pass

    def visit_guard(self, stmt: Guard):
        pass

    def visit_pattern_expr(self, stmt: PatternExpr):
        pass

    def visit_compare_pattern_expr(self, stmt: ComparePatternExpr):
        def _evaluate_compare_pattern(value: Literal) -> bool:
            return self._evaluate_binary_comparison(
                value,
                self.evaluate(stmt.right),
                stmt.operator
            )
        return _evaluate_compare_pattern

    def visit_type_pattern_expr(self, stmt: TypePatternExpr):
        def _evaluate_type_pattern(value: Literal) -> bool:
            if stmt.type == TokenType.STRING_TYPE:
                return isinstance(value, str)
            if stmt.type == TokenType.NUMBER_TYPE:
                return isinstance(value, (int, float))
            if stmt.type == TokenType.BOOL_TYPE:
                return isinstance(value, bool)
            if stmt.type == TokenType.NIL_TYPE:
                return value is None
        return _evaluate_type_pattern

    def visit_parameter(self, parameter: Parameter):
        pass

    def is_truthy(self, value: Literal) -> bool:
        if not value:
            return False
        return True

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def is_number(self, value: Literal | UserDefinedFunction) -> bool:
        return type(value) == int or type(value) == float

    def try_cast_to_number(
            self,
            value: Literal | UserDefinedFunction
    ) -> int | float | None:
        if isinstance(value, float) or isinstance(value, int):
            return value
        if not value or value is False:
            return 0
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        if value is True:
            return 1
        if isinstance(value, Callable):
            return self.try_cast_to_number(value.name)
        return None

    def cast_to_str(self, value: Literal | UserDefinedFunction):
        if value is None:
            return "nil"
        if value is True:
            return "true"
        if value is False:
            return "false"
        return str(value)
