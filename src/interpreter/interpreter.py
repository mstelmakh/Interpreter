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

from interpreter.models import Environment, Callable, Function
from interpreter.builtins import PrintFunction
from interpreter.exceptions import Return


class Interpreter(Visitor):
    def __init__(self):
        self.environment = Environment()
        self.environment.define("print", PrintFunction())

    def visit_program(self, program: Program):
        for statement in program.statements:
            self.evaluate(statement)

    def visit_assignment_expr(self, expr: AssignmentExpr):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_binary(self, expr: BinaryExpr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator:
            case TokenType.MINUS:
                return self._evaluate_binary_minus(left, right)
            case TokenType.PLUS:
                return self._evaluate_binary_plus(left, right)
            case TokenType.STAR:
                return self._evaluate_binary_multiply(left, right)
            case TokenType.SLASH:
                return self._evaluate_binary_divide(left, right)
            case (
                TokenType.GREATER_EQUAL
                | TokenType.GREATER
                | TokenType.LESS_EQUAL
                | TokenType.LESS
                | TokenType.EQUAL_EQUAL
                | TokenType.BANG_EQUAL
            ):
                return self._evaluate_binary_comparison(
                    left,
                    right,
                    expr.operator
                )
        return None

    def _evaluate_binary_minus(self, left, right):
        left = self.try_cast_to_number(left)
        right = self.try_cast_to_number(right)
        if left is not None and right is not None:
            return left - right
        raise RuntimeError("Operands must be coercible to numbers.")

    def _evaluate_binary_plus(self, left, right):
        if (
            (isinstance(left, str) and isinstance(right, str)) or
            (self.is_number(left) and self.is_number(right))
        ):
            return left + right
        if self.try_cast_to_number(left):
            new_right = self.try_cast_to_number(right)
            if new_right is not None:
                # 15 + "2"
                return left + new_right
            # 15 + "hello"
            return str(left) + right
        if self.try_cast_to_number(right):
            new_left = self.try_cast_to_number(left)
            if new_left is not None:
                # "2" + 15
                return new_left + right
            # "hello" + 15
            return left + str(right)
        left = self.try_cast_to_number(left)
        right = self.try_cast_to_number(right)
        return left + right

    def _evaluate_binary_multiply(self, left, right):
        left = self.try_cast_to_number(left)
        right = self.try_cast_to_number(right)
        if left is not None and right is not None:
            return left * right
        raise RuntimeError("Operands must be coercible to numbers.")

    def _evaluate_binary_divide(self, left, right):
        left = self.try_cast_to_number(left)
        right = self.try_cast_to_number(right)
        if left is not None and right is not None:
            return left / right
        raise RuntimeError("Operands must be coercible to numbers.")

    def _evaluate_binary_comparison(
            self,
            left,
            right,
            operator_type: TokenType
    ):
        if type(left) != type(right):
            if isinstance(left, str):
                new_left = self.try_cast_to_number(left)
                right = self.try_cast_to_number(right)
                if new_left is not None:
                    # "2" < 5
                    left = new_left
                else:
                    # "hello" < 5
                    right = str(right)
            elif isinstance(right, str):
                left = self.try_cast_to_number(left)
                new_right = self.try_cast_to_number(right)
                if new_right is not None:
                    # 5 < "2"
                    right = new_right
                else:
                    # 5 < "hello"
                    left = str(left)
            else:
                left = self.try_cast_to_number(left)
                right = self.try_cast_to_number(right)
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
        raise RuntimeError("Operator must be a comparison operator.")

    def visit_literal(self, expr: LiteralExpr):
        return expr.value

    def visit_unary(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)
        match expr.operator:
            case TokenType.MINUS:
                right = self.try_cast_to_number(right)
                if right:
                    return -right
                raise RuntimeError("Operand must be coercible to number.")
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
        return self.environment.get(expr.name)

    def visit_call(self, expr: CallExpr):
        callee: Callable = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, Callable):
            raise RuntimeError("Can only call functions.")
        if callee.arity is not None and len(arguments) != callee.arity:
            raise RuntimeError(
                f"Expected {callee.arity} arguments but got {len(arguments)}."
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
        function = Function(stmt, self.environment)
        self.environment.define(stmt.name, function)

    def visit_variable_stmt(self, stmt: VariableStmt):
        value = None
        if stmt.expression:
            value = self.evaluate(stmt.expression)
        self.environment.define(stmt.name, value, stmt.is_const)

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
        pass

    def visit_case_stmt(self, stmt: CaseStmt):
        pass

    def visit_guard(self, stmt: Guard):
        pass

    def visit_pattern_expr(self, stmt: PatternExpr):
        pass

    def visit_compare_pattern_expr(self, stmt: ComparePatternExpr):
        pass

    def visit_type_pattern_expr(self, stmt: TypePatternExpr):
        pass

    def visit_parameter(self, parameter: Parameter):
        pass

    def is_truthy(self, value: str | int | float | bool | None):
        if not value:
            return False
        return True

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def is_number(self, value: str | int | float | bool | None):
        return type(value) == int or type(value) == float

    def try_cast_to_number(self, value: str | int | float | bool | None):
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
        return None
