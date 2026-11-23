from dataclasses import dataclass


@dataclass(frozen=True)
class Row:
    date: str
    item: str
    amount: float


def parse_line(line: str) -> Row:
    raise NotImplementedError
