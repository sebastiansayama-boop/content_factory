from content_factory.artifacts import ArtifactStore
from content_factory.content_run_planner import ContentRunPlanner
from content_factory.runtime import Capability, ExecutionResult
from content_factory.runtime_store import RuntimeStore
from content_factory.workspace import ContentWorkspace


class FakeFactory:
    def __init__(self, output, tmp_path):
        self._store = RuntimeStore(tmp_path / "runtime.sqlite3")
        self._artifacts = ArtifactStore(tmp_path / "artifacts")
        self._capability = Capability(
            capability_id="fake.text.generate",
            input_contract=lambda item: None,
            executor=lambda item, execution_id: ExecutionResult(
                execution_id=execution_id,
                capability_id="fake.text.generate",
                output_revision_id=f"fake:{item.revision_id}",
                payload=output,
            ),
        )

    @staticmethod
    def _verify(_, execution):
        from content_factory.runtime import VerificationResult

        return VerificationResult(
            output_revision_id=execution.output_revision_id,
            passed=bool(str(execution.payload).strip()),
        )


def test_planner_uses_runtime_and_preserves_requested_formats(tmp_path):
    output = (
        '{"objective":"Explain the topic",'
        '"research_questions":["What evidence is needed?"],'
        '"source_requirements":["primary sources"],'
        '"deliverables":['
        '{"format":"long_video","purpose":"episode"},'
        '{"format":"telegram","purpose":"post"}],'
        '"editorial_constraints":["cite sources"],'
        '"quality_checks":["verify claims"]}'
    )
    factory = FakeFactory(output, tmp_path)
    workspace = ContentWorkspace(factory)
    result = ContentRunPlanner(workspace).plan(
        run_id="run-1",
        title="Thai spirits",
        brief="Explain Red Fanta offerings.",
        audience="General audience",
        goal="Create an episode",
        formats=["long_video", "telegram"],
        constraints=["cite sources"],
    )

    assert result["objective"] == "Explain the topic"
    assert {item["format"] for item in result["deliverables"]} == {"long_video", "telegram"}
    assert result["runtime"]["work_item_id"] == "content-run-plan-run-1"
    factory._store.close()
