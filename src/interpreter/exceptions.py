class Return(RuntimeError):
    def __init__(self, value: str | int | float | bool | None):
        self.value = value
