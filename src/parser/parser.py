from lexer.lexers import BaseLexer
from lexer.tokens import Token, TokenType, LITERALS

from parser.program import Program
from parser.data import (
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
    ExpressionStmt,
    ReturnStmt,
    Parameter,
    BlockStmt
)
from parser.exceptions import (
    ParserError,
    MissingLeftParenthesisError,
    MissingRightParenthesisError,
    MissingRightBraceError,
    MissingExpressionError,
    MissingArgumentError,
    MissingIfConditionError,
    MissingWhileConditionError,
    MissingFunctionNameError,
    MissingFunctionBodyError,
    MissingIfBodyError,
    MissingElseBodyError,
    MissingWhileBodyError,
    MissingVariableNameError,
    MissingSemicolonError,
    MissingParameterError,
    MissingParameterNameError,
    DuplicateParametersError
)

from typing import Callable


class Parser:
    # TODO: Handle Comments
    def __init__(self, lexer: BaseLexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()
        self.queue = []

    def parse_statement(self) -> Stmt | None:
        # declaration | expression_statement | if_statement |
        # while_statement | return_statement | match_statement
        return (
          self.parse_function_stmt() or
          self.parse_variable_stmt() or
          self.parse_if_stmt() or
          self.parse_while_stmt() or
          self.parse_return_stmt() or
          self.parse_expression_stmt()
        )

    def parse_function_stmt(self) -> FunctionStmt | None:
        # "fn" IDENTIFIER "(" [parameters] ")" block
        if not self.try_consume(TokenType.FUNCTION):
            return None

        name = self.consume(
            TokenType.IDENTIFIER,
            MissingFunctionNameError(self.current_token.position)
        ).value
        self.consume(
            TokenType.LEFT_PAREN,
            MissingLeftParenthesisError(self.current_token.position)
        )
        parameters = self.parse_parameters()
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        block = self.parse_block_stmt()
        if not block:
            raise MissingFunctionBodyError(name, self.current_token.position)
        return FunctionStmt(name, parameters, block)

    def parse_variable_stmt(self) -> VariableStmt | None:
        # ("var" | "const") IDENTIFIER ["=" logical_or] ";"
        if self.try_consume(TokenType.VAR):
            is_const = False
        elif self.try_consume(TokenType.CONST):
            is_const = True
        else:
            return None
        token = self.consume(
            TokenType.IDENTIFIER,
            MissingVariableNameError(self.current_token.position)
        )
        if not self.try_consume(TokenType.EQUAL):
            return VariableStmt(token, None, is_const)
        expr = self.parse_or()
        if not expr:
            raise MissingExpressionError(
                "Missing expression after '='",
                self.current_token.position
            )
        self.consume(
            TokenType.SEMICOLON,
            MissingSemicolonError(self.current_token.position)
        )
        return VariableStmt(token, expr, is_const)

    def parse_parameters(self) -> list[Parameter]:
        # parameter {"," parameter}
        parameters = []
        parameter = self.parse_parameter()
        if not parameter:
            return parameters
        parameters.append(parameter)
        while self.try_consume(TokenType.COMMA):
            parameter = self.parse_parameter()
            if not parameter:
                raise MissingParameterError(self.current_token.position)
            if parameter.name in [parameter.name for parameter in parameters]:
                raise DuplicateParametersError(
                    parameter.name,
                    self.current_token.position
                )
            parameters.append(parameter)
        return parameters

    def parse_parameter(self) -> Parameter | None:
        # ["const"] IDENTIFIER
        if self.try_consume(TokenType.CONST):
            name = self.consume(
                TokenType.IDENTIFIER,
                MissingParameterNameError(self.current_token.position)
            )
            return Parameter(name, True)
        if param := self.try_consume(TokenType.IDENTIFIER):
            return Parameter(param.value, False)
        return None

    def parse_if_stmt(self) -> IfStmt | None:
        # "if" "(" expression ")" (statement | block)
        # ["else" (statement | block)]
        if not self.try_consume(TokenType.IF):
            return None
        self.consume(
            TokenType.LEFT_PAREN,
            MissingLeftParenthesisError(self.current_token.position)
        )
        condition = self.parse_expression()
        if not condition:
            raise MissingIfConditionError(
                self.current_token.position,
                self.current_token.position
            )
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        body = self.parse_statement() or self.parse_block_stmt()
        if not body:
            raise MissingIfBodyError(
                self.current_token.position,
                self.current_token.position
            )
        if not self.try_consume(TokenType.ELSE):
            return IfStmt(condition, body, None)
        else_body = self.parse_statement() or self.parse_block_stmt()
        if not else_body:
            raise MissingElseBodyError(
                self.current_token.position,
                self.current_token.position
            )
        return IfStmt(condition, body, else_body)

    def parse_while_stmt(self) -> WhileStmt | None:
        # "while" "(" expression ")" (statement | block)
        if not self.try_consume(TokenType.WHILE):
            return None
        self.consume(
            TokenType.LEFT_PAREN,
            MissingLeftParenthesisError(self.current_token.position)
        )
        condition = self.parse_expression()
        if not condition:
            raise MissingWhileConditionError(
                self.current_token.position,
                self.current_token.position
            )
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        body = self.parse_statement() or self.parse_block_stmt()
        if not body:
            raise MissingWhileBodyError(
                self.current_token.position,
                self.current_token.position
            )
        return WhileStmt(condition, body)

    def parse_block_stmt(self) -> BlockStmt | None:
        # "{" {statement} "}"
        if not self.try_consume(TokenType.LEFT_BRACE):
            return None
        statements = []
        while statement := self.parse_statement():
            statements.append(statement)
        self.consume(
            TokenType.RIGHT_BRACE,
            MissingRightBraceError(self.current_token.position)
        )
        return BlockStmt(statements)

    def parse_return_stmt(self) -> ReturnStmt | None:
        # "return" [expression] ";"
        if not self.try_consume(TokenType.RETURN):
            return None
        expr = self.parse_expression()
        self.consume(
            TokenType.SEMICOLON,
            MissingSemicolonError(self.current_token.position)
        )
        return ReturnStmt(expr)

    def parse_expression_stmt(self) -> ExpressionStmt | None:
        # expression ";"
        expr = self.parse_expression()
        if not expr:
            return None
        self.consume(
            TokenType.SEMICOLON,
            MissingSemicolonError(self.current_token.position)
        )
        return ExpressionStmt(expr)

    def parse_expression(self) -> Expr | None:
        # assignment
        return self.parse_assignment()

    def parse_assignment(self) -> AssignmentExpr | None:
        # [IDENTIFIER "="] logical_or
        if not (token := self.try_consume(TokenType.IDENTIFIER)):
            return self.parse_or()
        if self.try_consume(TokenType.EQUAL):
            value = self.parse_or()
            return AssignmentExpr(token, value)
        self.queue.append(self.current_token)
        self.current_token = token
        return self.parse_or()

    def parse_or(self) -> LogicalExpr | None:
        # logical_and {"or" logical_and}
        expr = self.parse_and()
        if not expr:
            return None
        while operator := self.try_consume(TokenType.OR):
            right = self.parse_and()
            if not right:
                raise MissingExpressionError(
                    "Missing expression after 'or' statement",
                    self.current_token.position
                )
            expr = LogicalExpr(expr, operator, right)
        return expr

    def parse_and(self) -> LogicalExpr | None:
        # equality {"and" equality}
        expr = self.parse_comparison()
        if not expr:
            return None
        while operator := self.try_consume(TokenType.AND):
            right = self.parse_equality()
            if not right:
                raise MissingExpressionError(
                    "Missing expression after 'and' statement",
                    self.current_token.position
                )
            expr = LogicalExpr(expr, operator, right)
        return expr

    def parse_equality(self) -> BinaryExpr | None:
        # comparison {EQUALITY_SIGN comparison}
        return self._parse_binary(
            self.parse_comparison,
            [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]
        )

    def parse_comparison(self) -> BinaryExpr | None:
        # term [COMPARISON_SIGN term]
        return self._parse_binary(
            self.parse_term,
            [TokenType.GREATER, TokenType.GREATER_EQUAL,
             TokenType.LESS, TokenType.LESS_EQUAL]
        )

    def parse_term(self) -> BinaryExpr | None:
        # factor {("-" | "+") factor}
        return self._parse_binary(
            self.parse_factor,
            [TokenType.PLUS, TokenType.MINUS]
        )

    def parse_factor(self) -> BinaryExpr | None:
        # unary {("/" | "*") unary}
        return self._parse_binary(
            self.parse_unary,
            [TokenType.SLASH, TokenType.STAR]
        )

    def parse_unary(self):
        # ["not" | "-"] primary
        if (
            operator := self.try_consume(TokenType.MINUS) or
            self.try_consume(TokenType.NOT)
        ):
            right = self.parse_primary()
            if not right:
                raise MissingExpressionError(
                    "Missing unary expression",
                    self.current_token.position
                )
            return UnaryExpr(operator, right)
        return self.parse_primary()

    def parse_primary(self):
        # call | IDENTIFIER | LITERAL | "(" expression ")"
        return (
            self.parse_indentifier_or_call() or
            self.parse_literal() or
            self.parse_grouping()
        )

    def parse_indentifier_or_call(self) -> IdentifierExpr | CallExpr | None:
        # call = IDENTIFIER "(" [arguments] ")" {"(" [arguments] ")"}
        if not (identifier := self.try_consume(TokenType.IDENTIFIER)):
            return None
        if not (expr := self.finish_call(identifier)):
            return IdentifierExpr(identifier.value)
        while new_expr := self.finish_call(expr):
            expr = new_expr
        return expr

    def finish_call(self, expr: CallExpr) -> CallExpr | None:
        if not self.try_consume(TokenType.LEFT_PAREN):
            return None
        arguments = self.parse_arguments()
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        return CallExpr(expr, arguments)

    def parse_arguments(self) -> list[Expr]:
        # expression {"," expression}
        arguments = []
        argument = self.parse_expression()
        if not argument:
            return arguments
        arguments.append(argument)
        while self.try_consume(TokenType.COMMA):
            argument = self.parse_expression()
            if not argument:
                raise MissingArgumentError(self.current_token.position)
            arguments.append(argument)
        return arguments

    def parse_literal(self) -> LiteralExpr | None:
        # NUMBER | STRING | BOOLEAN | "nil"
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
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        return GroupingExpr(expr)

    def parse(self) -> Program:
        # {statement}, EOF
        statements = []
        while statement := self.parse_statement():
            statements.append(statement)
        print(statements)
        # TODO: error if not EOF?
        return Program(statements)

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
                raise MissingExpressionError(
                    "Missing second expression",
                    self.current_token.position
                )
            expr = BinaryExpr(expr, operator, right)
        return expr

    def try_consume(self, expected_type: TokenType) -> Token | None:
        try:
            return self.consume(expected_type, ParserError(None, None))
        except ParserError:
            return None

    def consume(self, expected_type: TokenType, error: ParserError) -> Token:
        if not self.current_token.type == expected_type:
            raise error
        current = self.current_token
        self.next_token()
        return current

    def next_token(self) -> Token:
        if self.queue:
            self.current_token = self.queue.pop(0)
        else:
            self.current_token = self.lexer.next_token()
