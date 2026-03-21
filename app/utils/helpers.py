def time_to_minutes(hhmm: str) -> int:
    """
    Convert "HH:MM" to minutes since 00:00.
    Simple helper if you later want human-readable times.
    """
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m
