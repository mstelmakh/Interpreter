from abc import ABC, abstractmethod
from typing import TextIO
from dataclasses import dataclass


@dataclass
class Stream(ABC):
    line: int = 1
    column: int = 0
    position: int = 0
    current_char: str = ''

    @abstractmethod
    def advance(self) -> str:
        pass


class FileStream(Stream):
    def __init__(self, file_handler: TextIO):
        self.file_handler = file_handler

    def advance(self) -> str:
        if self.current_char == "\n":
            self.column = 1
            self.line += 1
        else:
            self.column += 1
        self.position = self.file_handler.tell()
        self.current_char = self.file_handler.read(1)
        return self.current_char


class TextStream(Stream):
    def __init__(self, text: str):
        self.it = iter(text)

    def advance(self) -> str:
        if self.current_char == "\n":
            self.column = 1
            self.line += 1
        else:
            self.column += 1
        self.position += len(self.current_char.encode('utf-8'))
        self.current_char = next(self.it, '')
        return self.current_char
