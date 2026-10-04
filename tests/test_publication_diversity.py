from content_factory.publication_diversity import (
    choose_diverse_claim_set,
    is_sufficiently_distinct,
    max_publication_similarity,
    publication_similarity,
)


def test_publication_similarity_detects_near_duplicate():
    first = "В Риме этот календарь определял порядок праздников и месяцев. Его структура влияла на повседневную жизнь."
    second = "В Риме этот календарь определял порядок праздников и месяцев. Его устройство влияло на повседневную жизнь."
    assert publication_similarity(first, second) > 0.58
    assert not is_sufficiently_distinct(second, [first])


def test_publication_similarity_accepts_different_factual_emphasis():
    first = "Календарь определял порядок месяцев и праздников в Риме."
    second = "Средневековый автор описывал будущее через религиозные циклы и ожидание перемен."
    assert max_publication_similarity(second, [first]) < 0.58
    assert is_sufficiently_distinct(second, [first])


def test_choose_diverse_claim_set_prefers_less_overlap():
    candidates = [
        (0, {"claim-1", "claim-2"}),
        (1, {"claim-3", "claim-4"}),
        (2, {"claim-1", "claim-3"}),
    ]
    assert choose_diverse_claim_set(candidates, {"claim-1", "claim-2"}) == 1
