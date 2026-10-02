from content_factory.factory_control import FactoryControlStore


def test_control_plane_timeline_distribution_observation_learning_and_replay(tmp_path):
    store = FactoryControlStore(tmp_path / "control.sqlite3")
    store.record("run-1", "factory.started", status="RUNNING", actor="api")
    store.record("run-1", "qc.completed", output_refs=("qc-1",), evidence={"passed": True})
    events = store.timeline("run-1")
    assert [event.event_type for event in events] == ["factory.started", "qc.completed"]

    prepared = store.prepare_publication(
        "run-1",
        "telegram",
        "final.mp4",
        {
            "text": "hello",
            "artifact": "final.mp4",
            "artifact_ids": ["asset-1"],
            "destination": "chat-123",
            "provenance": {"run_id": "run-1", "claim_ids": ["claim-1"]},
        },
    )
    assert prepared["status"] == "PREPARED"
    assert prepared["destination"] == "chat-123"
    assert prepared["artifact_ids_json"] == '["asset-1"]'
    published = store.publish(prepared["publication_id"], run_status="APPROVED")
    assert published["status"] == "PUBLISHED"
    assert published["published_at"]
    assert published["external_id"].startswith("local-")
    assert published["response"]["mode"] == "local"

    observation = store.observe(
        prepared["publication_id"],
        {"views": 100, "retention": 0.72},
        source="test",
    )
    assert observation["observation_id"].startswith("obs-")

    learning = store.create_learning(
        "run-1",
        [observation["observation_id"]],
        "Short hooks may improve retention.",
        {"style_bible": {"hook": "front-load the claim"}},
    )
    assert learning["status"] == "CANDIDATE"
    promoted = store.promote_learning(learning["learning_id"], "human-learning-1")
    assert promoted["status"] == "PROMOTED"

    run = {
        "run_id": "run-1",
        "result": {
            "content_spec": {},
            "research": {},
            "editorial": {},
            "script": {},
            "production": {
                "assets": [
                    {"asset_id": "asset-1", "claim_refs": ["kc-1"]},
                    {"asset_id": "asset-2", "claim_refs": ["kc-2"]},
                ]
            },
        },
    }
    replay = store.replay_plan(
        run,
        changed_claim_ids=["kc-1"],
        content_brief={"brief_id": "brief-1", "title": "Version one"},
        content_brief_revision_id="brief-1-r1",
        changes={"style_bible": {"pace": "faster"}},
    )
    assert replay["regenerate_asset_ids"] == ["asset-1"]
    assert replay["content_brief_id"] == "brief-1"
    assert replay["content_brief_revision_id"] == "brief-1-r1"
    assert replay["content_brief"]["title"] == "Version one"
    assert replay["retain_asset_ids"] == ["asset-2"]
    assert replay["revise"] == ["content_spec.style_bible"]
    assert replay["rerun"] == ["production", "assembly", "qc", "approval", "export"]
    store.close()

def test_publication_requires_approved_content_run(tmp_path):
    from content_factory.state_machine import InvalidStateTransition

    store = FactoryControlStore(tmp_path / "control.sqlite3")
    prepared = store.prepare_publication(
        "run-guard",
        "telegram",
        "content-1",
        {"text": "hello", "destination": "chat-1"},
    )
    try:
        store.publish(prepared["publication_id"], run_status="REVIEW")
    except InvalidStateTransition:
        pass
    else:
        raise AssertionError("publication was allowed before ContentRun approval")
    assert store.list_publications("run-guard")[0]["status"] == "PREPARED"
    store.close()


def test_external_publication_failure_becomes_unknown(tmp_path):
    from content_factory.state_machine import InvalidStateTransition

    class BrokenPublisher:
        def publish(self, payload, *, publication_id):
            raise RuntimeError("telegram timeout")

    store = FactoryControlStore(tmp_path / "control.sqlite3")
    prepared = store.prepare_publication(
        "run-unknown",
        "telegram",
        "content-1",
        {"text": "hello", "destination": "chat-1"},
    )
    try:
        store.publish(
            prepared["publication_id"],
            run_status="APPROVED",
            publisher=BrokenPublisher(),
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("broken external publisher did not raise")
    publication = store.list_publications("run-unknown")[0]
    assert publication["status"] == "UNKNOWN"
    try:
        store.publish(publication["publication_id"], run_status="APPROVED", publisher=BrokenPublisher())
    except InvalidStateTransition:
        pass
    else:
        raise AssertionError("UNKNOWN publication was automatically retried")
    store.close()
