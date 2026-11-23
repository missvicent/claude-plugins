STORE: dict[str, str] = {}
DELETED: set[str] = set()


def add(code: str, url: str) -> None:
    STORE[code] = url


def delete(code: str) -> None:
    STORE.pop(code, None)
    DELETED.add(code)
