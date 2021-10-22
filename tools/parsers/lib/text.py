"""Helper modules for text manipulation in parsers."""
from typing import Dict, Iterable, Pattern


def search_all_patterns(patterns: Iterable[Pattern], text: str) -> Dict[str, str]:
    """Search a text for all patterns and extract the named groups."""
    extracted: Dict[str, str] = {}
    for pattern in patterns:
        match = pattern.search(text)
        if not match:
            continue
        for key, value in match.groupdict().items():
            if value:
                extracted[key] = value
    return extracted
