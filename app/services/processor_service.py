from __future__ import annotations

import re
from collections import Counter


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "into",
    "using",
    "study",
    "analysis",
    "toward",
    "over",
    "under",
    "between",
    "based",
    "their",
    "have",
    "has",
    "been",
    "were",
}


def reconstruct_abstract(abstract_inverted_index: dict | None) -> str | None:
    if not abstract_inverted_index:
        return None

    positions: list[tuple[int, str]] = []
    for word, indexes in abstract_inverted_index.items():
        for position in indexes:
            positions.append((position, word))

    if not positions:
        return None

    positions.sort(key=lambda item: item[0])
    return " ".join(word for _, word in positions)


def normalize_text(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    cleaned = re.sub(r"[^\w\s-]", "", cleaned, flags=re.UNICODE)
    return cleaned.lower() or None


def summarize_text(value: str | None, max_words: int = 45) -> str | None:
    if not value:
        return None
    words = value.split()
    if len(words) <= max_words:
        return value
    return " ".join(words[:max_words]) + "..."


def extract_keywords(*parts: str | None, limit: int = 12) -> list[str]:
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        normalized = normalize_text(part) or ""
        tokens.extend(
            token
            for token in normalized.split()
            if len(token) > 3 and token not in STOPWORDS and not token.isdigit()
        )

    if not tokens:
        return []

    counts = Counter(tokens)
    return [token for token, _ in counts.most_common(limit)]
