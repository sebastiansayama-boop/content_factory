import os

import pytest

from content_factory.openai_adapter import OpenAIResponsesAdapter


@pytest.mark.external
@pytest.mark.skipif(
    os.getenv("CF_RUN_EXTERNAL") != "1" or not os.getenv("OPENAI_API_KEY"),
    reason="set CF_RUN_EXTERNAL=1 and OPENAI_API_KEY to run the real provider proof",
)
def test_real_openai_execution():
    adapter = OpenAIResponsesAdapter()
    result = adapter.generate(
        "Return exactly one short sentence proving that the Content Factory provider boundary is reachable."
    )

    assert 200 <= result.status_code < 300
    assert result.response_id
    text = adapter.response_text(result)
    assert text.strip()
