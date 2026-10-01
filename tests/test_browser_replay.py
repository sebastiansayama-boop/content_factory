import pytest
from http.server import ThreadingHTTPServer
import threading

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
    monkeypatch.setenv("FACTORY_TELEGRAM_FAKE", "1")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "browser-fake-chat")
    monkeypatch.setattr(ProductHandler, "_rate_limited", lambda *args, **kwargs: False)
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


def test_browser_user_vertical_slice(factory_server, page):
    base_url, service = factory_server
    page.goto(base_url, wait_until="domcontentloaded")

    page.locator("#token").fill("browser-e2e-token")
    page.locator("#title").fill("Browser user vertical slice")
    page.locator("#source").fill(
        "Explain how volcanic lightning forms during explosive eruptions. "
        "Use evidence and write for a general reader."
    )

    page.locator("#runFactory").click()
    page.get_by_text("Research завершён · проверь знания", exact=True).wait_for()

    promote = page.locator("#knowledgeReview button[data-claim]").first
    assert promote.count() == 1
    promote.click()

    page.get_by_text("Готово · QC пройден", exact=True).wait_for()

    package = page.locator("#package")
    package.get_by_text("текст", exact=True).wait_for()
    assert package.locator("img[data-asset-id]").count() >= 2
    page.locator("img[data-asset-id]").first.wait_for()
    page.wait_for_function(
        """() => Array.from(document.querySelectorAll('img[data-asset-id]')).some(img => img.src.startsWith('blob:'))"""
    )

    assert page.locator("#approve").is_enabled()
    page.locator("#approve").click()
    page.get_by_text("Материал принят", exact=True).wait_for()

    page.locator("#export").click()
    page.get_by_text("Экспорт готов", exact=True).wait_for()
    download_button = page.locator("#downloadExport")
    assert download_button.count() == 1

    with page.expect_download() as download_info:
        download_button.click()
    download = download_info.value
    assert download.suggested_filename == "content-package.json"

    page.locator("#editInstruction").fill(
        "Сделай следующую версию менее рекламной и более объясняющей."
    )
    page.locator("#regenerate").click()
    page.get_by_text("Новая версия готова · QC пройден", exact=True).wait_for()

    assert page.locator("#package img[data-asset-id]").count() >= 2
    assert service.content_runs.list()
    runs = service.content_runs.list()
    assert len(runs) >= 2
    assert any(run.status == "REVIEW" for run in runs)


def test_browser_topic_to_package_edit_and_export(factory_server, page):
    base_url, service = factory_server
    page.goto(base_url, wait_until="domcontentloaded")

    page.locator("#token").fill("browser-e2e-token")
    page.locator("#source").fill(
        "Convergent evolution describes the independent emergence of similar functional traits "
        "in unrelated lineages facing similar environmental pressures."
    )
    page.locator('input[name="platform"][value="instagram"]').check()
    page.locator("#tone").select_option("analytical")
    page.locator("#length").select_option("short")

    page.locator("#runFactory").click()
    page.get_by_text("Research complete · knowledge review required", exact=True).wait_for()

    promote = page.locator("#knowledgeReview button[data-claim]").first
    assert promote.count() == 1
    promote.click()
    page.get_by_text("QC пройден · материал готов", exact=True).wait_for()

    run_id = page.locator("#runResult").inner_text().strip()
    assert run_id.startswith("run-")
    assert page.locator(".script").inner_text().strip()
    images = page.locator(".asset-card img")
    assert images.count() >= 1
    page.wait_for_function("document.querySelector(\'.asset-card img\')?.complete && document.querySelector(\'.asset-card img\').naturalWidth > 0")

    page.locator("#editInstruction").fill("Сделай начало более прямым и оставь только самый важный тезис.")
    page.locator("#regenerate").click()
    page.get_by_text("Новая версия готова · QC пройден", exact=True).wait_for()

    regenerated_run_id = page.locator("#runResult").inner_text().strip()
    assert regenerated_run_id.startswith("run-")
    assert regenerated_run_id != run_id
    assert service.content_runs.get(regenerated_run_id).status == "REVIEW"

    page.locator("#approve").click()
    page.get_by_text("Материал принят · экспорт доступен", exact=True).wait_for()

    page.locator("#export").click()
    page.get_by_text("Экспорт готов", exact=True).wait_for()
    assert page.locator("#lineage a[href*='/export/download']").count() == 1
    exported = service.content_runs.get(regenerated_run_id)
    assert exported is not None
    assert exported.status == "EXPORTED"
    assert exported.result["export"]["status"] == "EXPORTED"
