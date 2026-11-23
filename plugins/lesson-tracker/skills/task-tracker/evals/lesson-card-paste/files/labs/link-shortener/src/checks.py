from src.store import DELETED, STORE


def one_url_per_code() -> bool:
    return len(STORE) == len(set(STORE))


def never_reused(code: str) -> bool:
    return code not in STORE  # bug: ignores DELETED


def expired_status(expired: bool) -> int:
    return 410 if expired else 200


def count_visits(visits: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for v in visits:
        counts[v] = counts.get(v, 0) + 1
    return counts
