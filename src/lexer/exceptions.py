from lexer.streams import Position


class LexerError(Exception):
    def __init__(self, message: str, position: Position) -> None:
        super().__init__(message)
        self.position = position


class InvalidEscapeSequenceError(LexerError):
    def __init__(self, sequence: str, position: Position) -> None:
        super().__init__(
            "Invalid escape character: " +
            f"'\\{sequence}'",
            position
        )


class UnterminatedStringError(LexerError):
    def __init__(self, position: Position) -> None:
        super().__init__("Unterminated string", position)


class UnexpecterCharacterError(LexerError):
    def __init__(self, character: str, position: Position) -> None:
        super().__init__(f"Unexpected character: {character}", position)
