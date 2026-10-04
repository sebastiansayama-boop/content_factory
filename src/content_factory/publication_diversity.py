from __future__ import annotations

import re
from collections import Counter


_TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [token.casefold() for token in _TOKEN_RE.findall(text or "") if len(token) > 1]


def _ngrams(tokens: list[str], size: int = 3) -> Counter[str]:
    if len(tokens) < size:
        return Counter(tokens)
    return Counter(" ".join(tokens[index:index + size]) for index in range(len(tokens) - size + 1))


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    shared = set(left) & set(right)
    dot = sum(left[item] * right[item] for item in shared)
    left_norm = sum(value * value for value in left.values()) ** 0.5
    right_norm = sum(value * value for value in right.values()) ** 0.5
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def publication_similarity(left: str, right: str) -> float:
    """Return a deterministic lexical/phrase similarity score in [0, 1].

    This is deliberately model-independent. It is a guardrail for regeneration,
    not a semantic quality judge.
    """
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    token_similarity = _jaccard(set(left_tokens), set(right_tokens))
    phrase_similarity = _cosine(_ngrams(left_tokens), _ngrams(right_tokens))
    return 0.35 * token_similarity + 0.65 * phrase_similarity


def max_publication_similarity(candidate: str, previous: list[str] | tuple[str, ...]) -> float:
    if not previous:
        return 0.0
    return max(publication_similarity(candidate, item) for item in previous if str(item).strip())


def is_sufficiently_distinct(
    candidate: str,
    previous: list[str] | tuple[str, ...],
    *,
    threshold: float = 0.35,
) -> bool:
    return max_publication_similarity(candidate, previous) < threshold


def claim_overlap_score(candidate_refs: set[str], previous_refs: set[str]) -> float:
    return _jaccard(candidate_refs, previous_refs)


def choose_diverse_claim_set(
    candidates: list[tuple[int, set[str]]],
    previous_refs: set[str],
) -> int:
    """Choose the candidate with the lowest overlap with the previous claim set.

    The first candidate wins ties, keeping the existing deterministic behavior
    when no previous publication exists or all candidates use the same claims.
    """
    if not candidates:
        raise ValueError("at least one candidate is required")
    best_index, best_refs = candidates[0]
    best_score = claim_overlap_score(best_refs, previous_refs)
    for index, refs in candidates[1:]:
        score = claim_overlap_score(refs, previous_refs)
        if score < best_score:
            best_index, best_refs, best_score = index, refs, score
    return best_index
