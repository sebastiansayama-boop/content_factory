from content_factory.asset_executor import AssetExecutor
from content_factory.asset_jobs import AssetJobStore


def test_stub_executor_materializes_asset_candidate(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "stub")
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    plan = {
        "asset_requests": [
            {
                "asset_request_id": "request-1",
                "script_unit_id": "unit-1",
                "type": "visual",
                "claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "acceptance_criteria": ["preserve provenance"],
            }
        ]
    }
    jobs.create_from_plan("run-1", plan)

    result = AssetExecutor(jobs, tmp_path).execute_run("run-1")

    assert len(result) == 1
    assert result[0].status == "COMPLETED"
    assert result[0].result["provider"] == "stub"
    assert result[0].result["asset_id"].startswith("asset-")
    assert result[0].result["claim_refs"] == ["kc-1"]

    jobs.close()


def test_higgsfield_executor_downloads_completed_image_and_preserves_provenance(tmp_path, monkeypatch):
    import json

    class FakeResponse:
        def __init__(self, status, payload=None, raw=None):
            self.status = status
            self._payload = payload
            self._raw = raw

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            if self._raw is not None:
                return self._raw
            return json.dumps(self._payload).encode("utf-8")

    calls = []

    def fake_urlopen(request, timeout=30):
        calls.append((request.full_url, request.method, dict(request.header_items())))
        if request.method == "POST":
            return FakeResponse(
                200,
                {"request_id": "req-1", "status": "queued"},
            )
        if request.method == "GET" and request.full_url.endswith("/status"):
            if sum(1 for url, _, _ in calls if url.endswith("/status")) == 1:
                return FakeResponse(200, {"status": "processing"})
            return FakeResponse(
                200,
                {"status": "completed", "images": [{"url": "https://cdn.example/image.png"}]},
            )
        if request.method == "GET" and request.full_url == "https://cdn.example/image.png":
            return FakeResponse(200, raw=b"real-image-bytes")
        raise AssertionError(f"unexpected URL: {request.full_url}")

    monkeypatch.setattr("content_factory.asset_executor.urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("content_factory.asset_executor.time.sleep", lambda _: None)
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "higgsfield")
    monkeypatch.setenv("HF_KEY", "test-key")
    monkeypatch.setenv("HF_POLL_TIMEOUT_SECONDS", "10")
    monkeypatch.setenv("HF_POLL_INTERVAL_SECONDS", "0.1")

    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    jobs.create_from_plan(
        "run-1",
        {
            "asset_requests": [{
                "asset_request_id": "request-1",
                "script_unit_id": "unit-1",
                "type": "visual",
                "claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "acceptance_criteria": ["preserve provenance"],
            }]
        },
    )

    result = AssetExecutor(jobs, tmp_path).execute_run("run-1")

    assert len(result) == 1
    job = result[0]
    assert job.status == "COMPLETED"
    assert job.result["provider"] == "higgsfield"
    assert job.result["claim_refs"] == ["kc-1"]
    assert job.result["evidence_refs"] == ["ke-1"]
    assert (tmp_path / "asset_jobs" / "run-1" / "request-1.png").read_bytes() == b"real-image-bytes"
    assert job.result["metadata"]["provider_request_id"] == "req-1"
    assert job.result["metadata"]["source_url"] == "https://cdn.example/image.png"
    status_urls = [url for url, method, _ in calls if method == "GET" and url.endswith("/status")]
    assert status_urls == ["https://api.higgsfield.ai/requests/req-1/status"] * 2
    jobs.close()


def test_openverse_relevance_gate_prefers_matching_candidate():
    from content_factory.openverse_adapter import OpenverseImage

    candidates = [
        OpenverseImage(
            id="irrelevant",
            url="https://example.com/people.jpg",
            preview_url="https://example.com/people-thumb.jpg",
            title="People sitting outside",
            creator="x",
            license="cc-by",
        ),
        OpenverseImage(
            id="hyena",
            url="https://example.com/hyena.jpg",
            preview_url="https://example.com/hyena-thumb.jpg",
            title="Spotted hyena in African savanna",
            creator="x",
            license="cc-by",
        ),
    ]

    selected = AssetExecutor._select_relevant_openverse_candidate(
        "spotted hyena in African savanna",
        candidates,
    )

    assert selected is not None
    assert selected.id == "hyena"


def test_openverse_relevance_gate_rejects_unrelated_candidates():
    from content_factory.openverse_adapter import OpenverseImage

    candidates = [
        OpenverseImage(
            id="people",
            url="https://example.com/people.jpg",
            preview_url="https://example.com/people-thumb.jpg",
            title="People sitting outside",
            creator="x",
            license="cc-by",
        ),
        OpenverseImage(
            id="zebra",
            url="https://example.com/zebra.jpg",
            preview_url="https://example.com/zebra-thumb.jpg",
            title="Zebra and wildebeest in grassland",
            creator="x",
            license="cc-by",
        ),
    ]

    selected = AssetExecutor._select_relevant_openverse_candidate(
        "spotted hyena in African savanna",
        candidates,
    )

    assert selected is None


# Real image selection regression: vision must reject cruise metadata matches. [telegram-e2e]
def test_openverse_pipeline_uses_visual_gate_to_reject_nile_cruise(tmp_path, monkeypatch):
    from content_factory.openverse_adapter import OpenverseImage
    from content_factory.visual_relevance import VisualVerification

    class FakeResponse:
        def __init__(self, raw):
            self.raw = raw
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self, *args):
            return self.raw

    wrong = OpenverseImage(
        id="cruise",
        url="https://example.com/cruise.jpg",
        preview_url="https://example.com/cruise-thumb.jpg",
        title="Modern Nile Cruise",
        creator="x",
        license="cc0",
    )
    right = OpenverseImage(
        id="crocodile",
        url="https://example.com/crocodile.jpg",
        preview_url="https://example.com/crocodile-thumb.jpg",
        title="Nile crocodile resting on riverbank",
        creator="x",
        license="cc-by",
    )

    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "openverse")
    monkeypatch.setattr(
        "content_factory.asset_executor.OpenverseImageProvider.search",
        lambda self, query, limit=20: [wrong, right],
    )

    def fake_urlopen(request, timeout=30):
        if request.full_url.endswith("cruise-thumb.jpg"):
            return FakeResponse(b"wrong-thumbnail")
        if request.full_url.endswith("crocodile-thumb.jpg"):
            return FakeResponse(b"right-thumbnail")
        if request.full_url.endswith("crocodile.jpg"):
            return FakeResponse(b"right-original")
        raise AssertionError(request.full_url)

    monkeypatch.setattr("content_factory.asset_executor.urllib.request.urlopen", fake_urlopen)

    class FakeVerifier:
        def verify_candidates(self, query, candidates, images):
            assert query == "modern Nile crocodile resting on riverbank"
            assert {candidate.id for candidate in candidates} == {"cruise", "crocodile"}
            assert {item[0] for item in images} == {"cruise", "crocodile"}
            return [
                VisualVerification("cruise", "REJECT", 0.01, False, False, True, True, "ship, not crocodile"),
                VisualVerification("crocodile", "ACCEPT", 0.96, True, True, False, True, "crocodile visible"),
            ]

    monkeypatch.setattr("content_factory.asset_executor.GeminiVisualRelevanceVerifier", FakeVerifier)

    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    jobs.create_from_plan(
        "run-visual-1",
        {
            "asset_requests": [{
                "asset_request_id": "request-1",
                "script_unit_id": "unit-1",
                "type": "visual",
                "visual_intent": "modern Nile crocodile resting on riverbank",
                "claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "acceptance_criteria": ["preserve provenance"],
            }]
        },
    )

    result = AssetExecutor(jobs, tmp_path).execute_run("run-visual-1")
    job = result[0]

    assert job.status == "COMPLETED"
    assert job.result["path"].endswith("request-1.jpg")
    assert (tmp_path / "asset_jobs" / "run-visual-1" / "request-1.jpg").read_bytes() == b"right-original"
    verification = job.result["metadata"]["visual_verification"]
    assert verification["candidate_id"] == "crocodile"
    assert verification["decision"] == "ACCEPT"
    assert verification["forbidden_present"] is False
    jobs.close()
