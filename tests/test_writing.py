from __future__ import annotations

from content_factory.writing import (
    StyleLinter,
    WritingProfile,
    infer_context_profile,
)


def test_writing_profile_can_be_derived_from_reference_texts():
    profile = WritingProfile.from_texts(
        [
            "Это короткая фраза. А это немного более длинное предложение с примером.\n\n"
            "Ещё один абзац с несколькими словами."
        ],
        profile_id="personal-v1",
    )

    assert profile.profile_id == "personal-v1"
    assert profile.sentence_length == "mostly short sentences"
    assert profile.paragraph_length == "short paragraphs"


def test_context_profile_adapts_to_history_and_telegram():
    context = infer_context_profile(
        topic="How people in history imagined the future",
        audience="general",
        goal="explain",
        platform="telegram",
    )

    assert context.domain == "history_and_culture"
    assert context.intent == "explain"
    assert context.platform == "telegram"
    assert context.structure == "hook → short development blocks → closing thought"
    assert "separate documented fact from interpretation" in context.context_notes


def test_style_linter_removes_em_dash_and_reports_metrics():
    profile = WritingProfile(profile_id="test")
    linter = StyleLinter(profile, min_words=0)

    result = linter.check(
        "В 1900 году — это был привычный способ рассуждать о будущем. "
        "Но форма будущего менялась."
    )

    assert result.passed is True
    assert "—" not in result.normalized_text
    assert result.metrics["original_em_dash_count"] == 1
    assert result.metrics["em_dash_count"] == 0


def test_style_linter_detects_formulaic_ai_phrasing():
    profile = WritingProfile(profile_id="test")
    linter = StyleLinter(profile, min_words=0)

    result = linter.check(
        "Важно отметить, что этот пример полезен. "
        "В современном мире это особенно важно."
    )

    assert result.passed is False
    assert "forbidden_pattern_hits" in result.violations[0]


def test_writing_profile_overrides_default_forbidden_patterns():
    profile = WritingProfile(
        profile_id="custom",
        forbidden_patterns=("overused phrase",),
    )
    linter = StyleLinter(profile, min_words=0)

    result = linter.check(
        "This is an overused phrase in a sufficiently long sentence for testing."
    )

    assert result.passed is False
    assert any("forbidden_pattern_hits" in item for item in result.violations)
