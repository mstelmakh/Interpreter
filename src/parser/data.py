from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod

from lexer.tokens import Token


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_binary_expr(self)


@dataclass
class LiteralExpr(Expr):
    value: int | float | str | None

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_literal(self)


@dataclass
class UnaryExpr(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_unary(self)


@dataclass
class LogicalExpr(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_logical(self)


@dataclass
class GroupingExpr(Expr):
    expression: Expr

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_grouping(self)


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
    name: Token
    params: list[Parameter]
    block: BlockStmt

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_function_stmt(self)


@dataclass
class Parameter(Stmt):
    name: str
    is_const: bool

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_parameter(self)


class Visitor(ABC):
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
    def visit_block_stmt(stmt: BlockStmt):
        pass

    @abstractmethod
    def visit_function_stmt(stmt: FunctionStmt):
        pass

    @abstractmethod
    def visit_parameter(parameter: Parameter):
        pass
