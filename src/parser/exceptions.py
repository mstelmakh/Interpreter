from lexer.streams import Position


class ParserError(Exception):
    def __init__(self, message: str, position: Position) -> None:
        super().__init__(message)
        self.position = position


class InvalidSyntaxError(ParserError):
    pass


class MissingLeftParenthesisError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__(
            "Missing opening parenthesis",
            position
        )


class MissingRightParenthesisError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__(
            "Missing closing parenthesis",
            position
        )


class MissingLeftBraceError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__(
            "Missing opening brace",
            position
        )


class MissingRightBraceError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__(
            "Missing closing brace",
            position
        )


class MissingExpressionError(ParserError):
    def __init__(self, message: str, position: Position) -> None:
        super().__init__(message, position)


class MissingMatchArgumentsError(MissingExpressionError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing arguments for 'match' statement", position)


class MissingArgumentError(MissingExpressionError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing argument", position)


class MissingPatternError(MissingExpressionError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing pattern", position)


class MissingConditionError(MissingExpressionError):
    def __init__(self, statement: str, position: Position) -> None:
        super().__init__(
            f"Missing condition in '{statement}' statement",
            position
        )


class MissingIfConditionError(MissingExpressionError):
    def __init__(self, position: Position) -> None:
        super().__init__("if", position)


class MissingWhileConditionError(MissingExpressionError):
    def __init__(self, position: Position) -> None:
        super().__init__("while", position)


class MissingFunctionNameError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing function name", position)


class MissingFunctionBodyError(ParserError):
    def __init__(self, function_name: str, position: Position) -> None:
        super().__init__(
            f"Missing body in '{function_name}' function",
            position
        )


class MissingStatementBodyError(ParserError):
    def __init__(self, statement: str, position: Position) -> None:
        super().__init__(f"Missing body in '{statement}' statement", position)


class MissingIfBodyError(MissingStatementBodyError):
    def __init__(self, position: Position) -> None:
        super().__init__("if", position)


class MissingElseBodyError(MissingStatementBodyError):
    def __init__(self, position: Position) -> None:
        super().__init__("else", position)


class MissingWhileBodyError(MissingStatementBodyError):
    def __init__(self, position: Position) -> None:
        super().__init__("while", position)


class MissingCaseBodyError(MissingStatementBodyError):
    def __init__(self, position: Position) -> None:
        super().__init__("case", position)


class MissingVariableNameError(MissingStatementBodyError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing variable name", position)


class MissingSemicolonError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing semicolon", position)


class MissingColonError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing colon", position)


class MissingParameterError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing parameter", position)


class MissingParameterNameError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing parameter name", position)


class MissingPatternIdentifierError(ParserError):
    def __init__(self, position: Position) -> None:
        super().__init__("Missing pattern identifier", position)


class DuplicateParametersError(ParserError):
    def __init__(self, parameter_name: str, position: Position) -> None:
        super().__init__(
            f"Duplicate of '{parameter_name}' parameter",
            position
        )


class DuplicatePatternNamesError(ParserError):
    def __init__(self, pattern_name: str, position: Position) -> None:
        super().__init__(
            f"Duplicate of '{pattern_name}' name",
            position
        )
