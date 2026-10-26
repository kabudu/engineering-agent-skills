"""Split valid Unicode scalar text, preserving every nonempty line verbatim."""


def split_nonempty(text):
    return [line for line in text.splitlines() if line]
