import pytest

from content_factory.publication_text_rules import (
    format_publication_text_rules,
    resolve_publication_text_rules,
    validate_publication_text,
)


def test_publication_rules_normalize_style_length_tone_and_variation():
    rules = resolve_publication_text_rules([
        "style: Публицистический",
        "length: Коротко",
        "tone_strength: Сильный",
        "variation: История",
    ])

    assert rules.style == "journalistic"
    assert rules.length == "short"
    assert rules.tone_strength == "high"
    assert rules.variation == "story"
    assert rules.enforce_length is True
    prompt = format_publication_text_rules(rules)
    assert "Variation: story" in prompt
    assert "не используй длинное тире" in prompt.lower()
    assert "пиши как редактор" in prompt.lower()
    assert "шаблонную связку" in prompt.lower()
    assert "сохраняй единый авторский голос серии" in prompt.lower()


def test_publication_rules_reject_unsupported_values():
    with pytest.raises(ValueError, match="unsupported publication style"):
        resolve_publication_text_rules(["style: рекламный"])


def test_publication_rules_reject_em_dash():
    rules = resolve_publication_text_rules(["length: Коротко"])
    text = " ".join(["Факт"] * 120) + " — продолжение"
    with pytest.raises(ValueError, match="em dash"):
        validate_publication_text(text, rules)


def test_publication_rules_enforce_explicit_length():
    rules = resolve_publication_text_rules(["length: Коротко"])
    short = " ".join(["Факт"] * 30)
    with pytest.raises(ValueError, match="outside"):
        validate_publication_text(short, rules)


def test_publication_rules_do_not_enforce_length_without_explicit_setting():
    rules = resolve_publication_text_rules(["style: Естественный"])
    assert rules.enforce_length is False
