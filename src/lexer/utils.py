def is_digit(c: str) -> bool:
    if not len(c) == 1:
        return False
    return c >= '0' and c <= '9'


def is_alpha(c: str) -> bool:
    if not len(c) == 1:
        return False
    return (
        (c >= 'a' and c <= 'z') or
        (c >= 'A' and c <= 'Z') or
        c == '_'
    )


def is_alphanumeric(c: str) -> bool:
    if not len(c) == 1:
        return False
    return is_alpha(c) or is_digit(c)
