"""Full HTTP workflow with durable stores and real image bytes.

The fixture is explicitly NOT Luka and does not establish Luka's identity,
creative output quality, or external social-network delivery.
"""
import hashlib
import json
import threading
import zipfile
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

from PIL import Image

from content_factory.character import CharacterCatalog
from content_factory.content_package import review_digest
from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace


class RunningFactory:
    def __init__(self):
        self.service = FactoryService()
        ProductHandler.service = self.service
        ProductHandler.workspace = ContentWorkspace(self.service)
        ProductHandler.content_runs = self.service.content_runs
        ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), ProductHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def request(self, method, path, data=None, *, raw=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=15)
        payload = raw if raw is not None else json.dumps(data).encode() if data is not None else None
        connection.request(method, path, body=payload, headers={
            'Authorization': 'Bearer cycle-test-token', 'Content-Type': 'application/octet-stream' if raw else 'application/json'})
        response = connection.getresponse()
        content = response.read()
        status = response.status
        connection.close()
        if response.getheader('Content-Type', '').startswith('application/json'):
            content = json.loads(content)
        return status, content

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.service.close()


def fixture_character(tmp_path):
    profile_dir = tmp_path / 'repository/docs/character'
    profile_dir.mkdir(parents=True)
    image = tmp_path / 'reference.png'
    Image.new('RGB', (640, 800), (75, 140, 170)).save(image)
    sha = hashlib.sha256(image.read_bytes()).hexdigest()
    (profile_dir / 'manifest.json').write_text(json.dumps({
        'reference_id': 'test-reference', 'status': 'candidate_pending_human_identity_qc',
        'original': {'sha256': sha, 'width': 640, 'height': 800, 'filename': 'reference.png'}}))
    (profile_dir / 'character.json').write_text(json.dumps({
        'character_id': 'test-creator', 'slug': 'fixture-creator', 'display_name': 'Test Fixture',
        'status': 'draft', 'identity': {'adult': True, 'face_description': 'Non-person image fixture',
            'approved_references': [], 'reference_candidates': [
                {'reference_id': 'test-reference', 'manifest_path': 'docs/character/manifest.json'}]},
        'personality': {'traits': []}, 'open_decisions': ['personality', 'canonical reference']}))
    return profile_dir, image, sha


def test_character_image_caption_qc_edit_export_restart_experience_and_publication(tmp_path, monkeypatch):
    profile_dir, original, sha = fixture_character(tmp_path)
    data_dir = tmp_path / 'data'
    monkeypatch.setenv('FACTORY_CHARACTER_DIR', str(profile_dir))
    monkeypatch.setenv('FACTORY_DATA_DIR', str(data_dir))
    monkeypatch.setenv('FACTORY_PROVIDER', 'local')
    monkeypatch.setenv('FACTORY_API_TOKEN', 'cycle-test-token')
    monkeypatch.setenv('FACTORY_TELEGRAM_FAKE', '1')
    monkeypatch.delenv('PUBLISH_URL', raising=False)
    ProductHandler._authorized_requests.clear()
    factory = RunningFactory()
    try:
        status, profile = factory.request('GET', '/api/characters/fixture-creator')
        assert status == 200
        assert profile['inventory'][0]['verified'] is False
        status, uploaded = factory.request('POST', '/api/imports', raw=original.read_bytes())
        assert status == 201
        status, imported = factory.request('POST', '/api/characters/fixture-creator/references/import', {
            'reference_id': 'test-reference', 'path': uploaded['path']})
        assert status == 201 and imported['verified']
        assert imported['status'].startswith('candidate')
        status, created = factory.request('POST', '/api/runs', {
            'title': 'Everyday photo', 'brief': 'A quiet cafe photo and a short caption.',
            'character_id': 'fixture-creator', 'formats': ['social_post'], 'constraints': ['platform: instagram']})
        assert status == 201
        run_id = created['run_id']
        base = '/api/runs/' + run_id
        status, context = factory.request('POST', base + '/factory', {})
        assert status == 409 and context['candidates']
        status, accepted = factory.request('POST', '/api/knowledge/' + context['candidates'][0]['claim_id'] + '/promote', {'decision_ref': 'test-context-review'})
        assert status == 200
        status, queued = factory.request('POST', base + '/factory', {})
        assert status == 409, queued
        assert queued['run']['plan']['deliverables']
        assert len(queued['jobs']) == 1 and queued['jobs'][0]['asset_type'] == 'visual'
        status, imported = factory.request('POST', base + '/assets/import', {
            'job_id': queued['jobs'][0]['job_id'], 'path': uploaded['path'],
            'provenance': {'source': 'explicit test fixture, not a generated Luka photograph',
                'character_revision_id': created['character']['revision_id'], 'reference_id': 'test-reference'}})
        assert status == 201, imported
        status, produced = factory.request('POST', base + '/factory', {})
        assert status == 200, produced
        assert produced['qc']['passed'] is False  # no automatic identity acceptance
        status, denied = factory.request('POST', base + '/approve', {'decision_ref': 'premature', 'channel': 'instagram'})
        assert status == 400
        status, edited = factory.request('POST', base + '/package', {'text': 'A quiet moment. Virtual creator, test fixture.'})
        assert status == 200, edited
        status, repeated_factory = factory.request('POST', base + '/factory', {})
        assert status == 200 and repeated_factory['idempotent']
        assert repeated_factory['run']['result']['package']['text'] == 'A quiet moment. Virtual creator, test fixture.'
        status, package = factory.request('GET', base + '/package')
        assert status == 200
        review_context = package['character_review_context']
        review = {key: review_context[key] for key in ('character_revision_id', 'package_digest', 'asset_hashes')}
        review.update(approved=True, decision_ref='test-image-and-caption-review',
                      reference_id='test-reference', reference_sha256=sha)
        status, checked = factory.request('POST', base + '/qc', {'character_review': review})
        assert status == 200 and checked['qc']['passed'], checked
        status, edited_again = factory.request('POST', base + '/package', {'text': 'Another quiet moment. Virtual creator, test fixture.'})
        assert status == 200
        status, stale = factory.request('POST', base + '/qc', {})
        assert status == 200 and not stale['qc']['passed']
        status, package = factory.request('GET', base + '/package')
        review['package_digest'] = package['character_review_context']['package_digest']
        status, checked = factory.request('POST', base + '/qc', {'character_review': review})
        assert status == 200 and checked['qc']['passed'], checked
        status, approved = factory.request('POST', base + '/approve', {'decision_ref': 'test-final-approval', 'channel': 'instagram'})
        assert status == 200 and approved['status'] == 'APPROVED', approved
        factory.close()
        factory = RunningFactory()
        status, exported = factory.request('POST', base + '/export', {})
        assert status == 200 and exported['export']['artifact_type'] == 'photo_publication', exported
        archive = data_dir / 'exports' / run_id / exported['export']['artifact']
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == exported['export']['sha256']
        with zipfile.ZipFile(archive) as bundle:
            assert set(bundle.namelist()) == {'caption.txt', 'image-01.png', 'publication.json'}
            assert bundle.read('caption.txt').decode() == 'Another quiet moment. Virtual creator, test fixture.'
            assert hashlib.sha256(bundle.read('image-01.png')).hexdigest() == sha
        status, blocked = factory.request('POST', base + '/publish', {'channel': 'instagram'})
        assert status == 400 and 'export' in blocked['error']
        assert factory.service.content_runs.get(run_id).status == 'EXPORTED'
        status, publication = factory.request('POST', base + '/publish', {'channel': 'telegram', 'actor_id': 'test-final-approval'})
        assert status == 200, publication
        assert publication['response']['mode'] == 'fake-telegram'
        status, repeated = factory.request('POST', base + '/publish', {})
        assert status == 200 and repeated['idempotent']
        status, observation = factory.request('POST', base + '/observe', {
            'publication_id': publication['publication_id'], 'metrics': {'views': 10}, 'source': 'test-fixture'})
        assert status == 201
        status, learning = factory.request('POST', base + '/learn', {
            'observation_ids': [observation['observation_id']], 'hypothesis': 'Try a shorter caption', 'proposed_changes': {'caption': 'shorter'}})
        assert status == 201 and learning['status'] == 'CANDIDATE'
        status, regenerated = factory.request('POST', base + '/regenerate', {'instruction': 'Try a different everyday setting'})
        assert status == 201
        next_id = regenerated['run']['run_id']
        status, next_run = factory.request('POST', '/api/runs/' + next_id + '/factory', {})
        assert status == 409, next_run
        assert next_run['run']['result']['experience_refs']
        assert next_run['run']['character']['revision_id'] == created['character']['revision_id']
    finally:
        factory.close()


def test_luka_inventory_and_preview_rejection(tmp_path):
    root = Path(__file__).resolve().parents[1]
    catalog = CharacterCatalog(root / 'docs/character', tmp_path)
    snapshot = catalog.snapshot('luka')
    assert len(catalog.inventory(snapshot)) == 8
    assert not any(r['verified'] for r in catalog.inventory(snapshot))
    staging = tmp_path / 'imports'
    staging.mkdir()
    preview = staging / 'preview.jpg'
    preview.write_bytes((root / 'docs/character/references/luka-cafe-2026-10-08-face-preview.jpg').read_bytes())
    import pytest
    with pytest.raises(ValueError, match='checksum or dimensions'):
        catalog.import_reference('luka', 'luka-ref-2026-10-08-cafe-01', str(preview))
    with pytest.raises(ValueError, match='inside FACTORY_DATA_DIR/imports'):
        catalog.import_reference('luka', 'luka-ref-2026-10-08-cafe-01', str(root / 'pyproject.toml'))


import pytest


@pytest.mark.browser
def test_browser_character_import_edit_review_and_instagram_download(tmp_path, monkeypatch, page):
    profile_dir, image, _ = fixture_character(tmp_path)
    monkeypatch.setenv('FACTORY_CHARACTER_DIR', str(profile_dir))
    monkeypatch.setenv('FACTORY_DATA_DIR', str(tmp_path / 'browser-data'))
    monkeypatch.setenv('FACTORY_PROVIDER', 'local')
    monkeypatch.setenv('FACTORY_API_TOKEN', 'cycle-test-token')
    ProductHandler._authorized_requests.clear()
    factory = RunningFactory()
    try:
        page.goto(f'http://127.0.0.1:{factory.server.server_port}/')
        page.locator('#token').fill('cycle-test-token')
        page.locator('#loadCharacters').click()
        page.locator('#character option[value="test-creator"]').wait_for(state='attached')
        page.locator('#character').select_option('test-creator')
        page.locator('input[name="platform"][value="instagram"]').check()
        page.locator('#title').fill('Creator photo browser proof')
        page.locator('#source').fill('A quiet everyday photograph and caption, without invented biography.')
        page.locator('#runFactory').click()
        page.locator('#knowledgeReview button[data-claim]').first.click()
        page.locator('#characterImport').wait_for(state='visible')
        page.locator('#referenceFile').set_input_files(str(image))
        page.locator('#productionFile').set_input_files(str(image))
        page.locator('#importCharacter').click()
        page.locator('#reviewCharacter').wait_for(state='visible')
        assert page.locator('#approve').is_disabled()
        page.locator('#packageText').fill('A quiet moment. A virtual creator in an imagined everyday scene.')
        page.locator('#savePackage').click()
        page.get_by_text('QC не пройден · исправь материал', exact=True).wait_for()
        page.locator('#reviewCharacter').click()
        page.get_by_text('Готово · QC пройден', exact=True).wait_for()
        page.locator('#approve').click()
        page.get_by_text('Материал принят', exact=True).wait_for()
        page.locator('#export').click()
        page.get_by_text('Экспорт готов', exact=True).wait_for()
        assert page.locator('#publish').is_disabled()
        with page.expect_download() as info:
            page.locator('#downloadExport').click()
        download = info.value
        assert download.suggested_filename == 'instagram-publication.zip'
        with zipfile.ZipFile(download.path()) as bundle:
            assert bundle.read('caption.txt').decode() == 'A quiet moment. A virtual creator in an imagined everyday scene.'
            assert 'image-01.png' in bundle.namelist()
        assert len(factory.service.control.list_experiences()) >= 2
    finally:
        factory.close()


@pytest.mark.parametrize('library_name', [
    'future-series', 'computer-games-series', 'cinema-development-series', 'greek-pantheon-series', 'thai-spiritual-world'])
def test_existing_library_series_two_episodes_through_http(tmp_path, monkeypatch, library_name):
    from copy import deepcopy
    from scripts.publish_telegram_library import _prepare_run
    root = Path(__file__).resolve().parents[1]
    library = json.loads((root / f'library/telegram/{library_name}.json').read_text())
    monkeypatch.setenv('FACTORY_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('FACTORY_PROVIDER', 'local')
    monkeypatch.setenv('FACTORY_API_TOKEN', 'cycle-test-token')
    monkeypatch.setenv('FACTORY_TELEGRAM_FAKE', '1')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', 'fake-chat')
    ProductHandler._authorized_requests.clear()
    factory = RunningFactory()
    try:
        previous_id = None
        for episode in library['episodes'][:2]:
            payload = deepcopy(episode)
            payload['story_state'].update(series_id=library['series_id'], title=library['title'])
            run = _prepare_run(factory.service, payload, tmp_path, previous_id)
            assert run.character is None
            status, approved = factory.request('POST', f'/api/runs/{run.run_id}/approve', {
                'decision_ref': 'existing-library-proof', 'channel': 'telegram'})
            assert status == 200, approved
            status, published = factory.request('POST', f'/api/runs/{run.run_id}/publish', {})
            assert status == 200, published
            assert published['response']['mode'] == 'fake-telegram'
            final = factory.service.content_runs.get(run.run_id)
            assert final.status == 'PUBLISHED'
            assert final.result['package']['text'] == episode['text']
            assert final.result['package']['series']['previous_run_id'] == previous_id
            assert final.result['package']['series']['episode'] == episode['episode']
            previous_id = run.run_id
    finally:
        factory.close()
