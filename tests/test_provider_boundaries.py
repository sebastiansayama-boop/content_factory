from content_factory.assembly import QualityGate
from content_factory.free_research import FreeWebGeminiAdapter
from content_factory.gemini_adapter import GeminiOpenAICompatibleAdapter
from content_factory.openverse_adapter import OpenverseImageProvider
from content_factory.providers import ImageProvider, LLMProvider, QCProvider, ResearchProvider


def test_existing_gemini_adapter_is_an_llm_provider():
    assert isinstance(GeminiOpenAICompatibleAdapter(), LLMProvider)


def test_existing_gemini_research_adapter_is_a_research_provider():
    assert isinstance(FreeWebGeminiAdapter(gemini=GeminiOpenAICompatibleAdapter()), ResearchProvider)


def test_existing_quality_gate_is_a_qc_provider():
    assert isinstance(QualityGate(), QCProvider)


def test_openverse_adapter_is_an_image_provider():
    assert isinstance(OpenverseImageProvider(), ImageProvider)
