from interpreter.models import Callable


class PrintFunction(Callable):
    @property
    def arity(self):
        return None

    def call(self, interpreter, arguments):
        arguments = [self.stringify(arg) for arg in arguments]
        print(*arguments)

    def stringify(self, value):
        if value is None:
            return "nil"
        if value is True:
            return "true"
        if value is False:
            return "false"
        return str(value)
