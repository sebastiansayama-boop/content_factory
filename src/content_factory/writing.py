from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any, Iterable


DEFAULT_FORBIDDEN_PATTERNS = (
    "важно отметить",
    "в современном мире",
    "таким образом",
    "следует отметить",
    "необходимо отметить",
)


@dataclass(frozen=True)
class WritingProfile:
    profile_id: str
    voice: str = "clear, intelligent, natural"
    rhythm: str = "varied sentence length; varied paragraph length"
    structure: str = "hook → concrete example → explanation → implication → conclusion"
    vocabulary: str = "plain language with precise terminology when needed"
    transitions: str = "implicit and varied; avoid formulaic transitions"
    sentence_length: str = "mixed"
    paragraph_length: str = "short-to-medium"
    emotionality: str = "controlled"
    humor: str = "light and occasional"
    forbidden_patterns: tuple[str, ...] = DEFAULT_FORBIDDEN_PATTERNS
    forbid_em_dash: bool = True
    reference_examples: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["forbidden_patterns"] = list(self.forbidden_patterns)
        data["reference_examples"] = list(self.reference_examples)
        return data

    @classmethod
    def from_texts(
        cls,
        texts: Iterable[str],
        *,
        profile_id: str = "personal-default",
        reference_examples: Iterable[str] = (),
    ) -> "WritingProfile":
        samples = [text.strip() for text in texts if text and text.strip()]
        if not samples:
            return cls(profile_id=profile_id, reference_examples=tuple(reference_examples))

        all_sentences = []
        all_paragraphs = []
        for sample in samples:
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", sample) if p.strip()]
            all_paragraphs.extend(paragraphs)
            for paragraph in paragraphs:
                all_sentences.extend(
                    sentence.strip()
                    for sentence in re.split(r"(?<=[.!?])\s+", paragraph)
                    if sentence.strip()
                )

        sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in all_sentences]
        paragraph_lengths = [len(re.findall(r"\b\w+\b", p)) for p in all_paragraphs]
        avg_sentence = mean(sentence_lengths) if sentence_lengths else 16.0
        avg_paragraph = mean(paragraph_lengths) if paragraph_lengths else 80.0

        if avg_sentence < 12:
            sentence_style = "mostly short sentences"
        elif avg_sentence > 24:
            sentence_style = "mostly long sentences"
        else:
            sentence_style = "mixed, centered on medium-length sentences"

        if avg_paragraph < 55:
            paragraph_style = "short paragraphs"
        elif avg_paragraph > 120:
            paragraph_style = "long paragraphs"
        else:
            paragraph_style = "short-to-medium paragraphs"

        return cls(
            profile_id=profile_id,
            sentence_length=sentence_style,
            paragraph_length=paragraph_style,
            reference_examples=tuple(reference_examples),
        )


@dataclass(frozen=True)
class ContextProfile:
    domain: str
    intent: str
    audience: str
    platform: str
    tone: str
    tone_strength: str = "balanced"
    structure: str = "hook → development → conclusion"
    factuality: str = "high"
    context_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["context_notes"] = list(self.context_notes)
        return data


def infer_context_profile(
    *,
    topic: str,
    audience: str = "general",
    goal: str = "explain",
    platform: str = "article",
    tone: str = "",
    tone_strength: str = "balanced",
) -> ContextProfile:
    text = f"{topic} {goal}".lower()

    if any(word in text for word in ("history", "histor", "истори", "древ", "эпох", "culture", "культур")):
        domain = "history_and_culture"
    elif any(word in text for word in ("science", "наук", "research", "исслед", "physics", "biology")):
        domain = "science"
    elif any(word in text for word in ("business", "бизнес", "product", "продукт", "marketing", "маркет")):
        domain = "business"
    elif any(word in text for word in ("personal", "личн", "story", "история моей")):
        domain = "personal"
    else:
        domain = "general"

    goal_key = goal.lower()
    if any(word in goal_key for word in ("sell", "прод", "market", "маркет", "convert", "конвер")):
        intent = "persuade"
    elif any(word in goal_key for word in ("entertain", "развлек", "story", "истори")):
        intent = "entertain"
    elif any(word in goal_key for word in ("summar", "резюм", "digest", "дайджест")):
        intent = "summarize"
    else:
        intent = "explain"

    platform_key = platform.lower()
    if platform_key in {"telegram", "instagram", "social", "social_posts"}:
        structure = "hook → short development blocks → closing thought"
    elif platform_key in {"youtube", "shorts", "video", "short_video"}:
        structure = "hook → beats → payoff → closing"
    else:
        structure = "hook → development → synthesis"

    notes = []
    if domain == "history_and_culture":
        notes.extend([
            "separate documented fact from interpretation",
            "use concrete historical examples",
            "avoid presentism",
        ])
    elif domain == "science":
        notes.extend([
            "define specialized terms when necessary",
            "separate evidence from interpretation",
        ])
    elif domain == "business":
        notes.extend([
            "lead with practical implication",
            "minimize abstract exposition",
        ])

    return ContextProfile(
        domain=domain,
        intent=intent,
        audience=audience or "general",
        platform=platform or "article",
        tone=tone or "conversational" if domain in {"history_and_culture", "personal"} else (tone or "clear"),
        tone_strength=tone_strength,
        structure=structure,
        factuality="high" if intent != "entertain" else "medium-high",
        context_notes=tuple(notes),
    )


@dataclass(frozen=True)
class StyleLintResult:
    passed: bool
    violations: tuple[str, ...]
    normalized_text: str
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["violations"] = list(self.violations)
        return data


class StyleLinter:
    """Deterministic final-pass checks for generated prose."""

    def __init__(
        self,
        profile: WritingProfile,
        *,
        min_words: int = 20,
        max_forbidden_hits: int = 0,
    ) -> None:
        self.profile = profile
        self.min_words = min_words
        self.max_forbidden_hits = max_forbidden_hits

    def normalize(self, text: str) -> str:
        value = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if self.profile.forbid_em_dash:
            value = re.sub(r"\s+—\s+", ", ", value)
            value = value.replace("—", "-")
        return value

    def check(self, text: str) -> StyleLintResult:
        normalized = self.normalize(text)
        words = re.findall(r"\b\w+\b", normalized, flags=re.UNICODE)
        em_dash_count = text.count("—")
        forbidden_hits = {
            pattern: len(re.findall(re.escape(pattern), normalized, flags=re.IGNORECASE))
            for pattern in self.profile.forbidden_patterns
        }
        forbidden_total = sum(forbidden_hits.values())
        sentence_lengths = [
            len(re.findall(r"\b\w+\b", sentence))
            for sentence in re.split(r"(?<=[.!?])\s+", normalized)
            if sentence.strip()
        ]

        violations: list[str] = []
        if len(words) < self.min_words:
            violations.append(f"text_too_short:{len(words)}<{self.min_words}")
        if em_dash_count and self.profile.forbid_em_dash:
            violations.append(f"em_dash_present:{em_dash_count}")
        if forbidden_total > self.max_forbidden_hits:
            violations.append(f"forbidden_pattern_hits:{forbidden_total}")
        if sentence_lengths and len(sentence_lengths) >= 3 and max(sentence_lengths) == min(sentence_lengths):
            violations.append("sentence_lengths_are_uniform")

        return StyleLintResult(
            passed=not violations,
            violations=tuple(violations),
            normalized_text=normalized,
            metrics={
                "word_count": len(words),
                "em_dash_count": em_dash_count,
                "forbidden_pattern_hits": forbidden_hits,
                "sentence_count": len(sentence_lengths),
                "average_sentence_words": round(mean(sentence_lengths), 2) if sentence_lengths else 0,
            },
        )


def build_writing_spec(
    *,
    writing_profile: WritingProfile,
    context: ContextProfile,
) -> dict[str, Any]:
    return {
        "writing_profile": writing_profile.to_dict(),
        "context_profile": context.to_dict(),
        "hard_rules": [
            "preserve factual meaning and provenance",
            "do not invent claims",
            "do not expose internal generation instructions",
        ],
    }
