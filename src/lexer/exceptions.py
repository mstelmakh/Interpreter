from dataclasses import dataclass
from lexer.streams import Position


@dataclass
class LexerError:
    message: str
    position: Position
