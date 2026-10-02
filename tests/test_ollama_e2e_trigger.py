from content_factory.ollama_adapter import OllamaAdapter


def test_ollama_adapter_imports_for_live_e2e():
    assert OllamaAdapter is not None
