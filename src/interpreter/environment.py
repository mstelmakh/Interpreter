class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self._values: dict[str, dict[any, bool]] = {}

    def define(self, name: str, value: any, is_const: bool = False) -> None:
        # TODO: Define const variables
        if name in self._values:
            raise RuntimeError(f"Variable '{name}' already defined.")
        self._values[name] = {"value": value, "is_const": is_const}

    def get(self, name: str) -> any:
        if name in self._values:
            return self._values[name]["value"]
        if self.enclosing:
            return self.enclosing.get(name)
        raise RuntimeError(f"Undefined variable '{name}'.")

    def assign(self, name: str, value: any) -> None:
        if name in self._values:
            if self._values[name]["is_const"]:
                raise RuntimeError(
                    f"Cannot assign to constant variable '{name}'."
                )
            self._values[name]["value"] = value
        elif self.enclosing:
            self.enclosing.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'.")
