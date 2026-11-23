CALLS = 0


def fetch(city: str) -> dict:
    global CALLS
    CALLS += 1
    return {"city": city, "temp": 21}


if __name__ == "__main__":
    fetch("Lima")
    fetch("Lima")
    print("second call:", "cached" if CALLS == 1 else "network")
