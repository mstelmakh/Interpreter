from abc import ABC, abstractmethod
from typing import TextIO
from dataclasses import dataclass, field


@dataclass
class Position:
    line: int
    column: int
    offset: int
    filename: str | None = None


@dataclass
class Stream(ABC):
    position: Position = field(default_factory=lambda: Position(1, 0, 0))
    current_char: str = ''

    @abstractmethod
    def advance(self) -> str:
        pass


class FileStream(Stream):
    def __init__(self, file_handler: TextIO):
        super().__init__()
        self.file_handler = file_handler
        self.position.filename = file_handler.name

    def advance(self) -> str:
        if self.current_char == "\n":
            self.position.column = 1
            self.position.line += 1
        else:
            self.position.column += 1
        self.position.offset = self.file_handler.tell()
        self.current_char = self.file_handler.read(1)
        return self.current_char


class TextStream(Stream):
    def __init__(self, text: str):
        super().__init__()
        self.it = iter(text)

    def advance(self) -> str:
        if self.current_char == "\n":
            self.position.column = 1
            self.position.line += 1
        else:
            self.position.column += 1
        self.position.offset += len(self.current_char.encode('utf-8'))
        self.current_char = next(self.it, '')
        return self.current_char
