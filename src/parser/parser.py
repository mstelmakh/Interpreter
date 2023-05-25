from lexer.lexers import BaseLexer
from lexer.tokens import Token, TokenType, LITERALS, TYPES, COMPARISON_TYPES

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
          self.parse_function_declaration() or
          self.parse_variable_declaration() or
          self.parse_if() or
          self.parse_while() or
          self.parse_return() or
          self.parse_match() or
          self.parse_expression_stmt()
        )

    def parse_function_declaration(self) -> FunctionStmt | None:
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
        block = self.parse_block()
        if not block:
            raise MissingFunctionBodyError(name, self.current_token.position)
        return FunctionStmt(name, parameters, block)

    def parse_variable_declaration(self) -> VariableStmt | None:
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
        expr = None
        if self.try_consume(TokenType.EQUAL):
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
        return VariableStmt(token.value, expr, is_const)

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
            ).value
            return Parameter(name, True)
        if param := self.try_consume(TokenType.IDENTIFIER):
            return Parameter(param.value, False)
        return None

    def parse_if(self) -> IfStmt | None:
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
                self.current_token.position
            )
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        body = self.parse_statement() or self.parse_block()
        if not body:
            raise MissingIfBodyError(
                self.current_token.position
            )
        if not self.try_consume(TokenType.ELSE):
            return IfStmt(condition, body, None)
        else_body = self.parse_statement() or self.parse_block()
        if not else_body:
            raise MissingElseBodyError(
                self.current_token.position
            )
        return IfStmt(condition, body, else_body)

    def parse_while(self) -> WhileStmt | None:
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
                self.current_token.position
            )
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        body = self.parse_statement() or self.parse_block()
        if not body:
            raise MissingWhileBodyError(
                self.current_token.position
            )
        return WhileStmt(condition, body)

    def parse_block(self) -> BlockStmt | None:
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

    def parse_return(self) -> ReturnStmt | None:
        # "return" [expression] ";"
        if not self.try_consume(TokenType.RETURN):
            return None
        expr = self.parse_expression()
        self.consume(
            TokenType.SEMICOLON,
            MissingSemicolonError(self.current_token.position)
        )
        return ReturnStmt(expr)

    def parse_match(self) -> MatchStmt | None:
        # "match" "(" arguments ")" "{" {case_block} "}"
        if not self.try_consume(TokenType.MATCH):
            return None
        self.consume(
            TokenType.LEFT_PAREN,
            MissingLeftParenthesisError(self.current_token.position)
        )
        arguments = self.parse_arguments()
        if not arguments:
            raise MissingMatchArgumentsError(self.current_token.position)
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        self.consume(
            TokenType.LEFT_BRACE,
            MissingLeftBraceError(self.current_token.position)
        )
        case_blocks = self.parse_case_blocks()
        self.consume(
            TokenType.RIGHT_BRACE,
            MissingRightBraceError(self.current_token.position)
        )
        return MatchStmt(arguments, case_blocks)

    def parse_case_blocks(self) -> list[CaseStmt]:
        # {case_block}
        blocks = []
        while block := self.parse_case_block():
            blocks.append(block)
        return blocks

    def parse_case_block(self) -> CaseStmt | None:
        # "(" pattern_expression {"," pattern_expression} ")"
        # [guard] ":" (statement | block)
        if not self.try_consume(TokenType.LEFT_PAREN):
            return None
        patterns = self.parse_patterns()
        if not patterns:
            raise MissingExpressionError(
                "Missing pattern",
                self.current_token.position
            )
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        guard = self.parse_guard()
        self.consume(
            TokenType.COLON,
            MissingColonError(self.current_token.position)
        )
        body = self.parse_statement() or self.parse_block()
        if not body:
            raise MissingCaseBodyError(
                self.current_token.position
            )
        return CaseStmt(patterns, guard, body)

    def parse_guard(self) -> Guard | None:
        # "if" "(" expression ")"
        if not self.try_consume(TokenType.IF):
            return None
        self.consume(
            TokenType.LEFT_PAREN,
            MissingLeftParenthesisError(self.current_token.position)
        )
        condition = self.parse_expression()
        if not condition:
            raise MissingIfConditionError(self.current_token.position)
        self.consume(
            TokenType.RIGHT_PAREN,
            MissingRightParenthesisError(self.current_token.position)
        )
        return Guard(condition)

    def parse_patterns(self) -> list[PatternExpr]:
        # pattern_expression {"," pattern_expression}
        patterns = []
        pattern = self.parse_pattern_expr()
        if not pattern:
            return patterns
        patterns.append(pattern)
        while self.try_consume(TokenType.COMMA):
            pattern = self.parse_pattern_expr()
            if not pattern:
                raise MissingPatternError(self.current_token.position)
            if pattern.name and pattern.name in [
                pattern.name for pattern in patterns
            ]:
                raise DuplicatePatternNamesError(
                    pattern.name,
                    self.current_token.position
                )
            patterns.append(pattern)
        return patterns

    def parse_pattern_expr(self) -> PatternExpr | None:
        # ("_" | pattern) ["as" IDENTIFIER]
        if self.try_consume(TokenType.UNDERSCORE):
            pattern = None
        else:
            pattern = self.parse_pattern()
            if not pattern:
                return None
        if not self.try_consume(TokenType.AS):
            return PatternExpr(pattern, None)
        identifier = self.consume(
            TokenType.IDENTIFIER,
            MissingPatternIdentifierError(self.current_token.position)
        )
        return PatternExpr(pattern, identifier.value)

    def parse_pattern(self) -> Expr | None:
        # or_pattern
        return self.parse_or_pattern()

    def parse_or_pattern(self) -> Expr | None:
        # and_pattern {"or" and_pattern}
        expr = self.parse_and_pattern()
        if not expr:
            return None
        while operator := self.try_consume(TokenType.OR):
            right = self.parse_and_pattern()
            if not right:
                raise MissingExpressionError(
                    "Missing expression after 'or' statement",
                    self.current_token.position
                )
            expr = LogicalExpr(expr, operator.type, right)
        return expr

    def parse_and_pattern(self) -> Expr | None:
        # closed_pattern {"and" closed_pattern}
        # closed_pattern = compare_pattern | type_pattern
        expr = self.parse_type_pattern() or self.parse_compare_pattern()
        if not expr:
            return None
        while operator := self.try_consume(TokenType.AND):
            right = self.parse_type_pattern() or self.parse_compare_pattern()
            if not right:
                raise MissingExpressionError(
                    "Missing expression after 'and' statement",
                    self.current_token.position
                )
            expr = LogicalExpr(expr, operator.type, right)
        return expr

    def parse_compare_pattern(self) -> Expr | None:
        #  ["!=" | COMPARISON_SIGN] unary
        if any(
            operator := self.try_consume(expected)
            for expected in COMPARISON_TYPES + [TokenType.BANG_EQUAL]
        ):
            right = self.parse_unary()
            if not right:
                raise MissingExpressionError(
                    "Missing expression",
                    self.current_token.position
                )
            return ComparePatternExpr(operator.type, right)
        expr = self.parse_unary()
        if not expr:
            return None
        return ComparePatternExpr(TokenType.EQUAL_EQUAL, expr)

    def parse_type_pattern(self) -> TypePatternExpr | None:
        # TYPE
        if not any(
            token := self.try_consume(expected)
            for expected in TYPES
        ):
            return None
        return TypePatternExpr(token.type)

    def parse_expression_stmt(self) -> Expr | None:
        # expression ";"
        expr = self.parse_expression()
        if not expr:
            return None
        self.consume(
            TokenType.SEMICOLON,
            MissingSemicolonError(self.current_token.position)
        )
        return expr

    def parse_expression(self) -> Expr | None:
        # assignment
        return self.parse_assignment()

    def parse_assignment(self) -> Expr | None:
        # [IDENTIFIER "="] logical_or
        if not (token := self.try_consume(TokenType.IDENTIFIER)):
            return self.parse_or()
        if self.try_consume(TokenType.EQUAL):
            value = self.parse_or()
            if not value:
                raise MissingExpressionError(
                    "Missing expression after '='",
                    self.current_token.position
                )
            return AssignmentExpr(token.value, value)
        self.queue.append(self.current_token)
        self.current_token = token
        return self.parse_or()

    def parse_or(self) -> Expr | None:
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
            expr = LogicalExpr(expr, operator.type, right)
        return expr

    def parse_and(self) -> Expr | None:
        # equality {"and" equality}
        expr = self.parse_equality()
        if not expr:
            return None
        while operator := self.try_consume(TokenType.AND):
            right = self.parse_equality()
            if not right:
                raise MissingExpressionError(
                    "Missing expression after 'and' statement",
                    self.current_token.position
                )
            expr = LogicalExpr(expr, operator.type, right)
        return expr

    def parse_equality(self) -> Expr | None:
        # comparison {EQUALITY_SIGN comparison}
        return self._parse_binary(
            self.parse_comparison,
            [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]
        )

    def parse_comparison(self) -> Expr | None:
        # term [COMPARISON_SIGN term]
        expr = self.parse_term()
        if not expr:
            return None
        if any(
            operator := self.try_consume(token_type)
            for token_type in [
                TokenType.GREATER, TokenType.GREATER_EQUAL,
                TokenType.LESS, TokenType.LESS_EQUAL
            ]
        ):
            right = self.parse_term()
            if not right:
                raise MissingExpressionError(
                    "Missing second expression",
                    self.current_token.position
                )
            expr = BinaryExpr(expr, operator.type, right)
        return expr

    def parse_term(self) -> Expr | None:
        # factor {("-" | "+") factor}
        return self._parse_binary(
            self.parse_factor,
            [TokenType.PLUS, TokenType.MINUS]
        )

    def parse_factor(self) -> Expr | None:
        # unary {("/" | "*") unary}
        return self._parse_binary(
            self.parse_unary,
            [TokenType.SLASH, TokenType.STAR]
        )

    def parse_unary(self) -> Expr | None:
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
            return UnaryExpr(operator.type, right)
        return self.parse_primary()

    def parse_primary(self) -> Expr | None:
        # call | IDENTIFIER | LITERAL | "(" expression ")"
        return (
            self.parse_identifier_or_call() or
            self.parse_literal() or
            self.parse_grouping()
        )

    def parse_identifier_or_call(self) -> IdentifierExpr | CallExpr | None:
        # call = IDENTIFIER "(" [arguments] ")" {"(" [arguments] ")"}
        if not (identifier := self.try_consume(TokenType.IDENTIFIER)):
            return None
        identifier = IdentifierExpr(identifier.value)
        if not (expr := self.finish_call(identifier)):
            return identifier
        while new_expr := self.finish_call(expr):
            expr = new_expr
        return expr

    def finish_call(self, expr: IdentifierExpr | CallExpr) -> CallExpr | None:
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
        if self.try_consume(TokenType.TRUE):
            return LiteralExpr(True)
        if self.try_consume(TokenType.FALSE):
            return LiteralExpr(False)
        if any(
            token := self.try_consume(token_type)
            for token_type in LITERALS
        ):
            return LiteralExpr(token.value)
        return None

    def parse_grouping(self) -> GroupingExpr | None:
        # "(" expression ")"
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
        if not self.current_token.type == TokenType.EOF:
            raise InvalidSyntaxError(
                f"Unexpected token of type '{self.current_token.type}'",
                self.current_token.position
            )
        return Program(statements)

    def _parse_binary(
        self,
        parse_operand: Callable[[], None],
        operator_types: list[TokenType]
    ) -> Expr | None:
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
            expr = BinaryExpr(expr, operator.type, right)
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
