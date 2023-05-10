from dataclasses import dataclass

from parser.data import Stmt, Visitor


@dataclass
class Program:
    statements: list[Stmt]

    def accept(self, visitor: Visitor):
        return visitor.visit(self)
