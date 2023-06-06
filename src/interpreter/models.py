from __future__ import annotations

from parser.models import FunctionStmt
from interpreter.exceptions import (
    Return,
    UndefinedVariableError,
    ConstantRedefinitionError,
    RedefinitionError
)


class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self._values: dict[str, dict[any, bool]] = {}

    def define(self, name: str, value: any, is_const: bool = False) -> None:
        if name in self._values:
            raise RedefinitionError(name, position=None)
        self._values[name] = {"value": value, "is_const": is_const}

    def define_function(self, function: Callable) -> None:
        name = function.name
        if name in self._values:
            self.assign(name, function)
        else:
            self.define(name, function)

    def get(self, name: str) -> any:
        if name in self._values:
            return self._values[name]["value"]
        if self.enclosing:
            return self.enclosing.get(name)
        raise UndefinedVariableError(name, position=None)

    def assign(self, name: str, value: any) -> None:
        if name in self._values:
            if self._values[name]["is_const"]:
                raise ConstantRedefinitionError(name, position=None)
            self._values[name]["value"] = value
        elif self.enclosing:
            self.enclosing.assign(name, value)
        else:
            raise UndefinedVariableError(name, position=None)


class Callable:
    @property
    def name(self):
        raise NotImplementedError()

    @property
    def arity(self):
        raise NotImplementedError()

    def call(self, interpreter, arguments):
        raise NotImplementedError()

    def __str__(self):
        return self.name


class UserDefinedFunction(Callable):
    def __init__(self, declaration: FunctionStmt, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    @property
    def name(self):
        return self.declaration.name

    @property
    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.name, arg, param.is_const)
        try:
            interpreter.execute_block(
                self.declaration.block.statements,
                environment
            )
        except Return as return_value:
            return return_value.value
        return None
