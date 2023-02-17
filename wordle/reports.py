from typing import Iterable, Set


def unique_words_played(attempts_in_user_notation: Iterable[str]) -> Set[str]:
    """Converts history of user attempts to plain English,
    dropping duplicate words."""
    return set(w.lower().replace('?', '') for w in attempts_in_user_notation)
