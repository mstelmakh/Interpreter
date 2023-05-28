from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod

from lexer.tokens import TokenType


@dataclass
class Program:
    statements: list[Stmt]

    def accept(self, visitor: Visitor):
        return visitor.visit_program(self)


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass


@dataclass
class AssignmentExpr(Expr):
    name: str
    value: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_assignment_expr(self)


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: TokenType
    right: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_binary(self)


@dataclass
class LiteralExpr(Expr):
    value: int | float | str | None

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_literal(self)


@dataclass
class UnaryExpr(Expr):
    operator: TokenType
    right: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_unary(self)


@dataclass
class LogicalExpr(Expr):
    left: Expr
    operator: TokenType
    right: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_logical(self)


@dataclass
class GroupingExpr(Expr):
    expression: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_grouping(self)


@dataclass
class IdentifierExpr(Expr):
    name: str

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_identifier(self)


@dataclass
class CallExpr(Expr):
    callee: Expr
    arguments: list[Expr]

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_call(self)


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass


@dataclass
class BlockStmt(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_block_stmt(self)


@dataclass
class FunctionStmt(Stmt):
    name: str
    params: list[Parameter]
    block: BlockStmt

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_function_stmt(self)


@dataclass
class VariableStmt(Stmt):
    name: str
    expression: Expr | None
    is_const: bool

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_variable_stmt(self)


@dataclass
class IfStmt(Stmt):
    condition: Expr
    body: Stmt
    body_else: Stmt | None

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_if_stmt(self)


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_while_stmt(self)


@dataclass
class ReturnStmt(Stmt):
    expression: Expr | None

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_return_stmt(self)


@dataclass
class MatchStmt(Stmt):
    arguments: list[Expr]
    case_blocks: list[CaseStmt]

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_match_stmt(self)


@dataclass
class CaseStmt(Stmt):
    patterns: list[PatternExpr]
    guard: Guard | None
    body: Stmt

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_case_stmt(self)


@dataclass
class Guard(Stmt):
    # TODO: Stmt or Expr?
    condition: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_guard(self)


@dataclass
class PatternExpr(Expr):
    pattern: Expr | None
    name: str | None

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_pattern_expr(self)


@dataclass
class ComparePatternExpr(Expr):
    operator: TokenType | None
    right: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_compare_pattern_expr(self)


@dataclass
class TypePatternExpr(Expr):
    type: TokenType

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_type_pattern_expr(self)


@dataclass
class Parameter(Stmt):
    name: str
    is_const: bool

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_parameter(self)


class Visitor(ABC):
    @abstractmethod
    def visit_program(program: Program):
        pass

    @abstractmethod
    def visit_assignment_expr(expr: AssignmentExpr):
        pass

    @abstractmethod
    def visit_binary(expr: BinaryExpr):
        pass

    @abstractmethod
    def visit_literal(expr: LiteralExpr):
        pass

    @abstractmethod
    def visit_unary(expr: UnaryExpr):
        pass

    @abstractmethod
    def visit_logical(expr: LogicalExpr):
        pass

    @abstractmethod
    def visit_grouping(expr: GroupingExpr):
        pass

    @abstractmethod
    def visit_identifier(expr: IdentifierExpr):
        pass

    @abstractmethod
    def visit_call(expr: CallExpr):
        pass

    @abstractmethod
    def visit_block_stmt(stmt: BlockStmt):
        pass

    @abstractmethod
    def visit_function_stmt(stmt: FunctionStmt):
        pass

    @abstractmethod
    def visit_variable_stmt(stmt: VariableStmt):
        pass

    @abstractmethod
    def visit_if_stmt(stmt: IfStmt):
        pass

    @abstractmethod
    def visit_while_stmt(stmt: WhileStmt):
        pass

    @abstractmethod
    def visit_return_stmt(stmt: ReturnStmt):
        pass

    @abstractmethod
    def visit_match_stmt(stmt: MatchStmt):
        pass

    @abstractmethod
    def visit_case_stmt(stmt: CaseStmt):
        pass

    @abstractmethod
    def visit_guard(stmt: Guard):
        pass

    @abstractmethod
    def visit_pattern_expr(stmt: PatternExpr):
        pass

    @abstractmethod
    def visit_compare_pattern_expr(stmt: ComparePatternExpr):
        pass

    @abstractmethod
    def visit_type_pattern_expr(stmt: TypePatternExpr):
        pass

    @abstractmethod
    def visit_parameter(parameter: Parameter):
        pass
