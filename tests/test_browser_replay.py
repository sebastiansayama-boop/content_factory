import threading
import time

import pytest
from http.server import ThreadingHTTPServer

from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace


pytestmark = pytest.mark.browser


@pytest.fixture
def factory_server(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_PROVIDER", "local")
    monkeypatch.setenv("FACTORY_API_TOKEN", "browser-e2e-token")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    service = FactoryService()
    ProductHandler.service = service
    ProductHandler.workspace = ContentWorkspace(service)
    ProductHandler.content_runs = service.content_runs
    ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)

    server = ThreadingHTTPServer(("127.0.0.1", 0), ProductHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}/", service
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        service.close()


def test_browser_replay_exact_content_brief_revision(factory_server, page):
    base_url, service = factory_server
    page.goto(base_url, wait_until="domcontentloaded")

    page.locator("#token").fill("browser-e2e-token")
    page.locator("#title").fill("Browser replay E2E")
    page.locator("#source").fill(
        "Similar environmental pressures can produce similar traits in unrelated lineages. "
        "Convergent evolution describes this repeated emergence of similar functional solutions."
    )

    page.locator("#runFactory").click()
    page.get_by_text("Research complete · knowledge review required", exact=True).wait_for()

    promote = page.locator("#package button[data-claim]").first
    assert promote.count() == 1
    claim_id = promote.get_attribute("data-claim")
    assert claim_id

    promote.click()
    page.get_by_text("QC passed · awaiting approval", exact=True).wait_for()

    source_run_text = page.locator("#runResult").inner_text()
    source_run_id = source_run_text.splitlines()[0].strip()
    assert source_run_id.startswith("run-")

    revision = page.locator("#briefRevision")
    revision.wait_for()
    assert revision.locator("option").count() == 1
    revision_id = revision.locator("option").first.get_attribute("value")
    assert revision_id
    assert revision_id.endswith("-r1")

    page.locator("#replayBtn").click()
    page.get_by_text("Replay & lineage", exact=True).wait_for()

    replay_panel = page.locator("#replayPanel")
    replay_text = replay_panel.inner_text()
    assert f"Source run: {source_run_id}" in replay_text
    assert f"Revision: {revision_id}" in replay_text
    assert "QC: PASSED" in replay_text
    assert "Artifacts: " in replay_text

    replay_run_line = next(
        line for line in replay_text.splitlines() if line.startswith("Replay run:")
    )
    replay_run_id = replay_run_line.split(":", 1)[1].strip()
    assert replay_run_id.startswith("run-")
    assert replay_run_id != source_run_id

    page.locator("#showTrace").click()
    trace_box = page.locator("#traceBox")
    trace_box.wait_for()
    trace_text = trace_box.inner_text()
    assert "REPLAY" in trace_text
    assert "PRODUCTION" in trace_text
    assert "QC" in trace_text

    persisted = service.content_runs.get(replay_run_id)
    assert persisted is not None
    assert persisted.status == "REVIEW"
    assert persisted.result["content_brief"]["revision_id"] == revision_id
    assert persisted.result["production"]["qc"]["status"] == "PASSED"

    page.locator("#approve").click()
    page.locator("#publish").wait_for(state="attached")
    page.wait_for_function("document.querySelector('#publish').disabled === false")
    assert "Approved" in page.locator("#status").inner_text()
    publications = service.control.list_publications(replay_run_id)
    assert len(publications) == 1
    assert publications[0]["status"] == "PREPARED"

    page.locator("#publish").click()
    page.get_by_text("Published", exact=False).wait_for()
    published = service.content_runs.get(replay_run_id)
    assert published is not None
    assert published.status == "PUBLISHED"
    assert published.result["publication"]["status"] == "PUBLISHED"
    assert published.result["information_flow"]["publications"][0]["status"] == "PUBLISHED"
