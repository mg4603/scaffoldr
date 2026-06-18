from re import compile as re_compile

ANSI_ESCAPE = re_compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)
