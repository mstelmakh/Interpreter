from lexer.streams import Position


class RuntimeError(Exception):
    def __init__(self, message: str, position: Position):
        super().__init__(message)
        self.position = position


class Return(RuntimeError):
    def __init__(
            self,
            value: str | int | float | bool | None,
            position: Position
    ):
        self.value = value
        super().__init__(None, position)


class UndefinedVariableError(RuntimeError):
    def __init__(self, name: str, position: Position):
        super().__init__(
            f"Undefined variable '{name}'",
            position
        )


class UndefinedFunctionError(RuntimeError):
    def __init__(self, name: str, position: Position):
        super().__init__(
            f"Undefined function '{name}'",
            position
        )


class RedefinitionError(RuntimeError):
    def __init__(self, name: str, position: Position):
        super().__init__(
            f"'{name}' is already defined",
            position
        )


class ConstantRedefinitionError(RuntimeError):
    def __init__(self, name: str, position: Position):
        super().__init__(
            f"Cannot redefine constant '{name}'",
            position
        )


class NumberConversionError(RuntimeError):
    def __init__(self, value: str, position: Position):
        super().__init__(
            f"Cannot convert '{value}' to a number",
            position
        )


class DivisionByZeroError(RuntimeError):
    def __init__(self, position: Position):
        super().__init__(
            "Division by zero",
            position
        )


class InvalidArgumentNumberError(RuntimeError):
    def __init__(self, name: str, expected: int, got: int, position: Position):
        super().__init__(
            f"Invalid number of arguments for '{name}': "
            f"expected {expected}, got {got}",
            position
        )
