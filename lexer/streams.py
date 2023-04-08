from abc import ABC, abstractmethod
from typing import TextIO
from dataclasses import dataclass


@dataclass
class Stream(ABC):
    line: int = 1
    column: int = 0
    position: int = 0

    @abstractmethod
    def advance(self) -> str:
        pass


class FileStream(Stream):
    def __init__(self, file_handler: TextIO):
        self.file_handler = file_handler
        self.current_char = ''

    def advance(self) -> str:
        if self.current_char == "\n":
            self.column = 0
            self.line += 1
        else:
            self.column += 1
        self.current_char = self.file_handler.read(1)
        self.position = self.file_handler.tell() - 1
        return self.current_char


class TextStream(Stream):
    def __init__(self, text: str):
        self.it = iter(text)
        self.next_item = next(self.it, '')

    def advance(self) -> str:
        current = self.next_item
        if current == "\n":
            self.column = 0
            self.line += 1
        else:
            self.column += 1
        self.next_item = next(self.it, '')
        self.position += 1
        return current
