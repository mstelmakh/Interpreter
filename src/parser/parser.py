from lexer.lexers import BaseLexer
from lexer.tokens import Token, TokenType

from parser.program import Program
from parser.data import Stmt, FunctionStmt, Parameter, BlockStmt


class Parser:
    def __init__(self, lexer: BaseLexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        return self.parse_or()

    def parse_or(self):
        return self.parse_and()

    def parse_and(self):
        return self.parse_equality()

    def parse_equality(self):
        expr = self.parse_comparison()

    def parse_comparison(self):
        return self.parse_term()

    def parse_term(self):
        return self.parse_factor()

    def parse_factor(self):
        return self.parse_unary()

    def parse_unary(self):
        return self.parse_primary()

    def parse_primary(self):
        return (
            self.parse_call() or
            self.parse_identifier() or
            self.parse_literal() or
            self.parse_grouping()
        )

    def parse_call(self):
        pass

    def parse_identifier(self):
        pass

    def parse_literal(self):
        pass

    def parse_grouping(self):
        pass

    def parse_function_stmt(self) -> FunctionStmt | None:
        # "fn" IDENTIFIER "(" [parameters] ")" block
        if not self.try_consume(TokenType.FUNCTION):
            return None

        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LEFT_PAREN)
        parameters = self.parse_parameters()
        self.consume(TokenType.RIGHT_PAREN)
        block = self.parse_block()
        if not block:
            # TODO: Error
            pass
        return FunctionStmt(name, parameters, block)

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
                pass
            if parameter.name in [parameter.name for parameter in parameters]:
                # TODO: Error
                pass
            parameters.append(parameter)
        return parameters

    def parse_parameter(self) -> Parameter | None:
        if self.try_consume(TokenType.CONST):
            name = self.consume(TokenType.IDENTIFIER)
            return Parameter(name, True)
        if param := self.try_consume(TokenType.IDENTIFIER):
            return Parameter(param.value, False)
        return None

    def parse_block(self) -> BlockStmt | None:
        if not self.try_consume(TokenType.LEFT_BRACE):
            return None
        statements = []
        statement = self.parse_statement()
        while statement:
            statements.append(statement)
            statement = self.parse_statement()
        self.consume(TokenType.RIGHT_BRACE)
        return BlockStmt(statements)

    def parse_statement(self) -> Stmt | None:
        pass

    def parse(self) -> Program:
        statements = []
        self.next_token()
        while statement := self.parse_statement():
            statements.append(statement)
        return Program(statements)

    def try_consume(self, expected_type: TokenType) -> Token | None:
        try:
            return self.consume(expected_type)
        # TODO: Error Type
        except _ as _:
            return None

    def consume(self, expected_type: TokenType) -> Token:
        if not self.current_token.type == expected_type:
            raise ValueError()
        current = self.current_token
        self.next_token()
        return current

    def next_token(self) -> Token:
        self.current_token = self.lexer.next_token()
