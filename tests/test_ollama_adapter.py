from content_factory.integrations import ExternalCallResult
from content_factory.ollama_adapter import OllamaAdapter, OllamaConfig
from content_factory.providers import LLMProvider


def test_ollama_adapter_is_an_llm_provider():
    adapter = OllamaAdapter.__new__(OllamaAdapter)
    assert isinstance(adapter, LLMProvider)


def test_ollama_response_text():
    result = ExternalCallResult("ollama.generate", 200, None, {"response": '{"title":"Test","content":"hello"}'})
    assert OllamaAdapter.response_text(result) == '{"title":"Test","content":"hello"}'


def test_ollama_generate_payload_without_network():
    class FakeHttp:
        def __init__(self):
            self.payload = None

        def call(self, payload):
            self.payload = payload
            return ExternalCallResult("ollama.generate", 200, None, {"response": "{}"})

    adapter = OllamaAdapter.__new__(OllamaAdapter)
    adapter.config = OllamaConfig(model="test:model")
    adapter._http = FakeHttp()
    result = adapter.generate("hello")
    assert result.status_code == 200
    assert adapter._http.payload["model"] == "test:model"
    assert adapter._http.payload["stream"] is False
    assert adapter._http.payload["format"] == "json"
