from content_factory.publication_text_matrix import TEXT_VARIATION_MATRIX, format_text_variation_matrix
from content_factory.publication_text_rules import resolve_publication_text_rules


def test_text_variation_matrix_is_fixed_and_nonempty():
    assert len(TEXT_VARIATION_MATRIX) >= 8
    ids = [item.id for item in TEXT_VARIATION_MATRIX]
    assert len(ids) == len(set(ids))
    matrix = format_text_variation_matrix()
    for item in TEXT_VARIATION_MATRIX:
        assert item.id in matrix
        assert item.opening in matrix


def test_publication_variation_defaults_to_model_selection():
    rules = resolve_publication_text_rules(["language: Русский"])
    assert rules.variation == "auto"
    assert any("модель" in item.casefold() for item in rules.instructions)


def test_explicit_variation_remains_available():
    rules = resolve_publication_text_rules(["variation: история"])
    assert rules.variation == "story"
