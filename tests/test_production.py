from content_factory.production import (
    Artifact,
    ProductionJob,
    ProductionJobStatus,
    ProductionRegistry,
)


class FakeProvider:
    def __init__(self, provider="fake"):
        self.provider = provider
        self.calls = 0

    def run(self, registry, *, capability_id, input_artifact_ids, output_specs):
        self.calls += 1
        job_id = f"job-{self.calls}"
        provider_job_id = f"{self.provider}-run-{self.calls}"
        job = registry.add_job(
            ProductionJob(
                job_id=job_id,
                capability_id=capability_id,
                provider=self.provider,
                provider_job_id=provider_job_id,
                input_artifact_ids=tuple(input_artifact_ids),
                parameters={"call": self.calls},
            )
        )
        outputs = [
            Artifact(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                revision_id=f"{job_id}-revision",
                reference=f"fake://{artifact_id}",
                producer_job_id=job.job_id,
            )
            for artifact_id, artifact_type in output_specs
        ]
        return registry.complete_job(job.job_id, outputs)


def test_production_job_and_artifact_contract_invalidates_exact_downstream_job():
    registry = ProductionRegistry()
    provider = FakeProvider()

    upstream = provider.run(
        registry,
        capability_id="generate-source-assets",
        input_artifact_ids=(),
        output_specs=[("asset-a-v1", "image"), ("asset-b-v1", "image")],
    )

    downstream = provider.run(
        registry,
        capability_id="compose-video",
        input_artifact_ids=upstream.output_artifact_ids,
        output_specs=[("asset-video-v1", "video")],
    )

    unrelated = provider.run(
        registry,
        capability_id="unrelated-output",
        input_artifact_ids=(),
        output_specs=[("asset-unrelated-v1", "image")],
    )

    assert upstream.status is ProductionJobStatus.SUCCEEDED
    assert downstream.status is ProductionJobStatus.SUCCEEDED
    assert unrelated.status is ProductionJobStatus.SUCCEEDED
    assert upstream.output_artifact_ids == ("asset-a-v1", "asset-b-v1")

    registry.add_artifact(
        Artifact(
            artifact_id="asset-a-v2",
            artifact_type="image",
            revision_id="upstream-r2",
            reference="fake://asset-a-v2",
            producer_job_id=upstream.job_id,
            metadata={"supersedes": "asset-a-v1"},
        )
    )

    invalidated = registry.invalidate_jobs_consuming("asset-a-v1")

    assert invalidated == (downstream.job_id,)
    assert registry.jobs[downstream.job_id].status is ProductionJobStatus.INVALIDATED
    assert registry.jobs[unrelated.job_id].status is ProductionJobStatus.SUCCEEDED
    assert registry.jobs[upstream.job_id].status is ProductionJobStatus.SUCCEEDED


def test_invalidated_downstream_job_can_be_regenerated_against_replacement_artifact():
    registry = ProductionRegistry()
    provider = FakeProvider()

    upstream = provider.run(
        registry,
        capability_id="generate-source-assets",
        input_artifact_ids=(),
        output_specs=[("asset-a-v1", "image"), ("asset-b-v1", "image")],
    )
    downstream = provider.run(
        registry,
        capability_id="compose-video",
        input_artifact_ids=upstream.output_artifact_ids,
        output_specs=[("asset-video-v1", "video")],
    )

    registry.add_artifact(
        Artifact(
            artifact_id="asset-a-v2",
            artifact_type="image",
            revision_id="upstream-r2",
            reference="fake://asset-a-v2",
            producer_job_id=upstream.job_id,
            metadata={"supersedes": "asset-a-v1"},
        )
    )
    registry.invalidate_jobs_consuming("asset-a-v1")

    regenerated = provider.run(
        registry,
        capability_id="compose-video",
        input_artifact_ids=("asset-a-v2", "asset-b-v1"),
        output_specs=[("asset-video-v2", "video")],
    )

    assert registry.jobs[downstream.job_id].status is ProductionJobStatus.INVALIDATED
    assert regenerated.status is ProductionJobStatus.SUCCEEDED
    assert regenerated.input_artifact_ids == ("asset-a-v2", "asset-b-v1")
    assert regenerated.output_artifact_ids == ("asset-video-v2",)
    assert registry.jobs[regenerated.job_id].provider_job_id == "fake-run-3"
    assert registry.jobs[regenerated.job_id].status is not ProductionJobStatus.INVALIDATED
