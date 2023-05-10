from lexer.lexers import BaseLexer
from lexer.tokens import Token, TokenType, LITERALS

from parser.program import Program
from parser.data import (
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
    ExpressionStmt,
    ReturnStmt,
    Parameter,
    BlockStmt
)

from typing import Callable


class Parser:
    def __init__(self, lexer: BaseLexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self) -> AssignmentExpr | None:
        # IDENTIFIER "=" logical_or
        if not (token := self.try_consume(TokenType.IDENTIFIER)):
            return None
        self.consume(TokenType.EQUAL)
        value = self.parse_or()
        return AssignmentExpr(token, value)

    def parse_or(self) -> LogicalExpr | None:
        expr = self.parse_and()
        if not expr:
            return None
        while operator := self.try_consume(TokenType.OR):
            right = self.parse_and()
            if not right:
                # TODO: Error
                print("Missing operand after 'or' statement.")
                return
            expr = LogicalExpr(expr, operator, right)
        return expr

    def parse_and(self) -> LogicalExpr | None:
        expr = self.parse_comparison()
        if not expr:
            return None
        while operator := self.try_consume(TokenType.AND):
            right = self.parse_equality()
            if not right:
                # TODO: Error
                print("Missing operand after 'and' statement.")
                return
            expr = LogicalExpr(expr, operator, right)
        return expr

    def _parse_binary(
            self,
            parse_operand: Callable[[], None],
            operator_types: list[TokenType]
    ) -> BinaryExpr | None:
        expr = parse_operand()
        if not expr:
            return None
        while any(
            operator := self.try_consume(token_type)
            for token_type in operator_types
        ):
            right = parse_operand()
            if not right:
                # TODO: Error
                print("Missing second operand in expression.")
                return
            expr = BinaryExpr(expr, operator, right)
        return expr

    def parse_equality(self) -> BinaryExpr | None:
        return self._parse_binary(
            self.parse_comparison,
            [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]
        )

    def parse_comparison(self) -> BinaryExpr | None:
        return self._parse_binary(
            self.parse_term,
            [TokenType.GREATER, TokenType.GREATER_EQUAL,
             TokenType.LESS, TokenType.LESS_EQUAL]
        )

    def parse_term(self) -> BinaryExpr | None:
        return self._parse_binary(
            self.parse_factor,
            [TokenType.PLUS, TokenType.MINUS]
        )

    def parse_factor(self) -> BinaryExpr | None:
        return self._parse_binary(
            self.parse_unary,
            [TokenType.SLASH, TokenType.STAR]
        )

    def parse_unary(self):
        if (
            operator := self.try_consume(TokenType.MINUS) or
            self.try_consume(TokenType.NOT)
        ):
            right = self.parse_primary()
            if not right:
                # TODO: Error
                print("Missing unary operand.")
                return
            return UnaryExpr(operator, right)
        return self.parse_primary()

    def parse_primary(self):
        return (
            self.parse_indentifier_or_call() or
            self.parse_literal() or
            self.parse_grouping()
        )

    def parse_indentifier_or_call(self) -> IdentifierExpr | CallExpr | None:
        # TODO: Call Expression
        # IDENTIFIER "(" [arguments] ")" {"(" [arguments] ")"}
        if not (identifier := self.try_consume(TokenType.IDENTIFIER)):
            return None
        if not self.try_consume(TokenType.LEFT_PAREN):
            return IdentifierExpr(identifier.value)
        arguments = self.parse_arguments()
        self.consume(TokenType.RIGHT_PAREN)
        while self.try_consume(TokenType.LEFT_PAREN):
            arguments = self.parse_arguments()
            self.consume(TokenType.RIGHT_PAREN)
        return

    def parse_literal(self) -> LiteralExpr | None:
        if any(
            token := self.try_consume(token_type)
            for token_type in LITERALS
        ):
            return LiteralExpr(token.value)
        return None

    def parse_grouping(self) -> GroupingExpr | None:
        if not self.try_consume(TokenType.LEFT_PAREN):
            return None
        expr = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN)
        return GroupingExpr(expr)

    def parse_function_stmt(self) -> FunctionStmt | None:
        # "fn" IDENTIFIER "(" [parameters] ")" block
        if not self.try_consume(TokenType.FUNCTION):
            return None

        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LEFT_PAREN)
        parameters = self.parse_parameters()
        self.consume(TokenType.RIGHT_PAREN)
        block = self.parse_block_stmt()
        if not block:
            # TODO: Error
            print("Missing function body.")
            return
        return FunctionStmt(name, parameters, block)

    def parse_variable_stmt(self) -> VariableStmt | None:
        # ("var" | "const") IDENTIFIER ["=" logical_or] ";"
        if self.try_consume(TokenType.VAR):
            is_const = False
        elif self.try_consume(TokenType.CONST):
            is_const = True
        else:
            return None
        token = self.consume(TokenType.IDENTIFIER)
        if not self.try_consume(TokenType.EQUAL):
            return VariableStmt(token, None, is_const)
        expr = self.parse_or()
        if not expr:
            # TODO: Error
            print("No expression after assignment.")
            return
        self.consume(TokenType.SEMICOLON)
        return VariableStmt(token, expr, is_const)

    def parse_parameters(self) -> list[Parameter]:
        parameters = []
        parameter = self.parse_parameter()
        if not parameter:
            return parameters
        parameters.append(parameter)
        while self.try_consume(TokenType.COMMA):
            parameter = self.parse_parameter()
            if not parameter:
                # TODO: Error
                print("Missing parameter after comma.")
                return
            if parameter.name in [parameter.name for parameter in parameters]:
                # TODO: Error
                print("Duplication of parameters.")
                return
            parameters.append(parameter)
        return parameters

    def parse_parameter(self) -> Parameter | None:
        if self.try_consume(TokenType.CONST):
            name = self.consume(TokenType.IDENTIFIER)
            return Parameter(name, True)
        if param := self.try_consume(TokenType.IDENTIFIER):
            return Parameter(param.value, False)
        return None

    def parse_block_stmt(self) -> BlockStmt | None:
        if not self.try_consume(TokenType.LEFT_BRACE):
            return None
        statements = []
        while statement := self.parse_statement():
            statements.append(statement)
        self.consume(TokenType.RIGHT_BRACE)
        return BlockStmt(statements)

    def parse_statement(self) -> Stmt | None:
        return (
          self.parse_if_stmt() or
          self.parse_while_stmt() or
          self.parse_return_stmt() or
          self.parse_function_stmt() or
          self.parse_variable_stmt() or
          self.parse_expression_stmt()
        )

    def parse_expression_stmt(self) -> ExpressionStmt | None:
        expr = self.parse_expression()
        if not expr:
            return None
        self.consume(TokenType.SEMICOLON)
        return ExpressionStmt(expr)

    def parse_return_stmt(self) -> ReturnStmt | None:
        if not self.try_consume(TokenType.RETURN):
            return None
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return ReturnStmt(expr)

    def parse_if_stmt(self) -> IfStmt | None:
        if not self.try_consume(TokenType.IF):
            return None
        self.consume(TokenType.LEFT_PAREN)
        condition = self.parse_expression()
        if not condition:
            # TODO: Error
            print("Missing if statement condition.")
            return
        body = self.parse_statement() or self.parse_block_stmt()
        if not body:
            # TODO: Error
            print("Missing if statement body.")
            return
        if not self.try_consume(TokenType.ELSE):
            return IfStmt(condition, body, None)
        else_body = self.parse_statement() or self.parse_block_stmt()
        if not else_body:
            # TODO: Error
            print("Missing else body.")
            return
        return IfStmt(condition, body, else_body)

    def parse_while_stmt(self) -> WhileStmt | None:
        if not self.try_consume(TokenType.WHILE):
            return None
        self.consume(TokenType.LEFT_PAREN)
        condition = self.parse_expression()
        if not condition:
            # TODO: Error
            print("Missing while statement condition.")
            return
        body = self.parse_statement() or self.parse_block_stmt()
        if not body:
            # TODO: Error
            print("Missing if statement body.")
            return
        return WhileStmt(condition, body)

    def parse(self) -> Program:
        statements = []
        while statement := self.parse_statement():
            statements.append(statement)
        print(statements)
        return Program(statements)

    def try_consume(self, expected_type: TokenType) -> Token | None:
        try:
            return self.consume(expected_type)
        # TODO: Error Type
        except:
            return None

    def consume(self, expected_type: TokenType) -> Token:
        if not self.current_token.type == expected_type:
            # TODO: Error Type
            raise ValueError()
        current = self.current_token
        self.next_token()
        return current

    def next_token(self) -> Token:
        self.current_token = self.lexer.next_token()
