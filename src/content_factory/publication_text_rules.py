from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicationTextRules:
    style: str
    length: str
    tone_strength: str
    variation: str
    min_chars: int
    max_chars: int
    instructions: tuple[str, ...]


_STYLE_ALIASES = {
    "естественный": "natural",
    "natural": "natural",
    "деловой": "business",
    "business": "business",
    "объясняющий": "explanatory",
    "explanatory": "explanatory",
    "публицистический": "journalistic",
    "journalistic": "journalistic",
}

_LENGTH_ALIASES = {
    "коротко": "short",
    "short": "short",
    "средне": "medium",
    "medium": "medium",
    "подробно": "long",
    "long": "long",
}

_TONE_ALIASES = {
    "слабый": "low",
    "low": "low",
    "средний": "medium",
    "medium": "medium",
    "сильный": "high",
    "high": "high",
}

_VARIATION_ALIASES = {
    "основной": "default",
    "default": "default",
    "история": "story",
    "story": "story",
    "разбор": "analysis",
    "analysis": "analysis",
}

_LENGTH_LIMITS = {
    "short": (500, 1000),
    "medium": (900, 1800),
    "long": (1500, 3000),
}


def _constraint(constraints: list[str] | tuple[str, ...], prefix: str, default: str) -> str:
    prefix = prefix.casefold() + ":"
    for item in constraints:
        value = str(item).strip()
        if value.casefold().startswith(prefix):
            return value.split(":", 1)[1].strip()
    return default


def _normalize(value: str, aliases: dict[str, str], label: str) -> str:
    normalized = aliases.get(value.casefold())
    if normalized is None:
        raise ValueError(f"unsupported publication {label}: {value}")
    return normalized


def resolve_publication_text_rules(constraints: list[str] | tuple[str, ...]) -> PublicationTextRules:
    style = _normalize(_constraint(constraints, "style", "natural"), _STYLE_ALIASES, "style")
    length = _normalize(_constraint(constraints, "length", "medium"), _LENGTH_ALIASES, "length")
    tone_strength = _normalize(
        _constraint(constraints, "tone_strength", "medium"),
        _TONE_ALIASES,
        "tone_strength",
    )
    variation = _normalize(
        _constraint(constraints, "variation", "default"),
        _VARIATION_ALIASES,
        "variation",
    )

    style_rules = {
        "natural": "Пиши живым современным языком. Избегай канцелярита и рекламных клише.",
        "business": "Пиши сдержанно и структурно. Убирай эмоциональные усилители и рекламные формулировки.",
        "explanatory": "Сначала объясняй смысл, затем детали. Термины раскрывай простыми словами.",
        "journalistic": "Используй сильный, но точный заход и ритм журналистского текста без сенсационности.",
    }
    tone_rules = {
        "low": "Эмоциональная выразительность минимальна; приоритет у ясности и фактов.",
        "medium": "Допускается умеренная выразительность, но факты и точность важнее эффекта.",
        "high": "Используй заметную эмоциональную динамику, но не преувеличивай факты и не создавай ложной срочности.",
    }
    variation_rules = {
        "default": "Основной вариант: прямой объясняющий текст с ясным развитием мысли.",
        "story": "Вариант-история: начинай с конкретной сцены, детали или исторического поворота и веди читателя к выводу.",
        "analysis": "Вариант-разбор: строй текст вокруг вопроса, причин, различий и вывода; меньше повествовательных украшений.",
    }
    return PublicationTextRules(
        style=style,
        length=length,
        tone_strength=tone_strength,
        variation=variation,
        min_chars=_LENGTH_LIMITS[length][0],
        max_chars=_LENGTH_LIMITS[length][1],
        instructions=(
            style_rules[style],
            tone_rules[tone_strength],
            variation_rules[variation],
            "Не используй длинное тире (—); перестраивай фразу через запятую, двоеточие или отдельное предложение.",
            "Не начинай текст с «Вы знали?», «Знаете ли вы?», «Did you know?» или их близких шаблонов без явного запроса пользователя.",
            "Не добавляй факты, которых нет в принятой knowledge/evidence базе.",
            "Не превращай вероятностные, ограниченные или контекстные утверждения в абсолютные.",
        ),
    )


def format_publication_text_rules(rules: PublicationTextRules) -> str:
    return "\n".join(
        [
            f"Style: {rules.style}",
            f"Length: {rules.length} ({rules.min_chars}-{rules.max_chars} characters of final publication text)",
            f"Tone strength: {rules.tone_strength}",
            f"Variation: {rules.variation}",
            "Publication rules:",
            *[f"- {item}" for item in rules.instructions],
        ]
    )


def validate_publication_text(text: str, rules: PublicationTextRules) -> None:
    normalized = text.strip()
    if not normalized:
        raise ValueError("publication text must not be empty")
    if "—" in normalized:
        raise ValueError("publication text must not contain em dash")
    if len(normalized) < rules.min_chars or len(normalized) > rules.max_chars:
        raise ValueError(
            f"publication text length {len(normalized)} is outside "
            f"{rules.min_chars}-{rules.max_chars} characters for {rules.length}"
        )
