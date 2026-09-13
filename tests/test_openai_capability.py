from content_factory.openai_capability import openai_text_capability
from content_factory.openai_adapter import OpenAIResponsesConfig
from content_factory.integrations import ExternalCallResult


class FakeOpenAI:
    def generate(self, prompt):
        assert prompt == "generate one test item"
        return ExternalCallResult(
            integration_id="openai.responses",
            status_code=200,
            response_id="resp-test-1",
            payload={
                "output": [
                    {
                        "content": [
                            {"text": "generated test item"},
                        ]
                    }
                ]
            },
        )

    @staticmethod
    def response_text(result):
        return result.payload["output"][0]["content"][0]["text"]


def test_openai_capability_binds_provider_response_to_execution_result():
    capability = openai_text_capability(FakeOpenAI())
    item = type(
        "Item",
        (),
        {
            "requested_outcome": "generate one test item",
        },
    )()

    capability.input_contract(item)
    execution = capability.executor(item, "exec-1")

    assert execution.execution_id == "exec-1"
    assert execution.capability_id == "openai.text.generate"
    assert execution.output_revision_id == "openai-response:resp-test-1"
    assert execution.payload == "generated test item"
    assert execution.evidence_refs == ("resp-test-1",)
