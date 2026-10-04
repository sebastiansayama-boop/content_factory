from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / '.control-result.json'
COMMANDS = {
    'status': ['python','-m','pytest','-q','tests/test_runtime.py','--disable-warnings'],
    'test': ['python','-m','pytest','-q','tests'],
    'product-test': ['python','-m','pytest','-q','tests/test_product_http_routes.py'],
    'visual-test': ['python','-m','pytest','-q','tests/test_visual_relevance.py'],
    'policy-test': ['python','-m','pytest','-q','tests/test_access_policy.py'],
    'telegram-test': ['python','-m','pytest','-s','-q','tests/test_telegram_historical_material_smoke.py::test_real_telegram_generated_historical_material_smoke','-m','external'],
    'telegram-matrix-5': ['python','-m','pytest','-s','-q','tests/test_telegram_historical_material_smoke.py::test_real_telegram_five_matrix_publications','-m','external'],
    'publication-test': ['python','-m','pytest','-q','tests/test_provider_e2e.py::test_live_historical_publication_text_variations_without_images','-m','external'],
    'editorial-test': ['python','-m','pytest','-s','-q','tests/test_editorial_method_benchmark.py','-m','external'],
    'telegram-series-episode-2': ['python','-m','pytest','-s','-q','tests/test_telegram_historical_material_smoke.py::test_real_telegram_series_episode_2_continuity','-m','external'],
    'telegram-series-episode-3': ['python','-m','pytest','-s','-q','tests/test_telegram_historical_material_smoke.py::test_real_telegram_series_episode_3_continuity','-m','external'],
    'telegram-series-episode-3-retry': ['python','-m','pytest','-s','-q','tests/test_telegram_historical_material_smoke.py::test_real_telegram_series_episode_3_continuity','-m','external'],
}
def parse():
    title = os.environ.get('ISSUE_TITLE','')
    body = os.environ.get('ISSUE_BODY','') or ''
    raw = title.removeprefix('control:').strip() if title.startswith('control:') else body.strip()
    command = raw.splitlines()[0].strip().lower()
    if command not in COMMANDS:
        print('Unsupported command: %r' % command, file=sys.stderr)
        print('Allowed: ' + ', '.join(sorted(COMMANDS)), file=sys.stderr)
        return 2
    with open(os.environ['GITHUB_OUTPUT'],'a',encoding='utf-8') as f: f.write('command='+command+'\n')
    return 0
def execute():
    command = os.environ.get('CONTROL_COMMAND','').strip().lower()
    # External commands have side effects (notably Telegram publication).
    # Re-running the same GitHub Actions attempt must never publish again.
    external_commands = {'telegram-test', 'telegram-matrix-5', 'publication-test', 'editorial-test', 'telegram-series-episode-2'}

    if not command:
        title = os.environ.get('ISSUE_TITLE','')
        raw = title.removeprefix('control:').strip() if title.startswith('control:') else (os.environ.get('ISSUE_BODY','') or '').strip()
        command = raw.splitlines()[0].strip().lower() if raw else ''
    if command not in COMMANDS:
        print('Unsupported command: %r' % command, file=sys.stderr)
        return 2
    if command in external_commands and os.environ.get('GITHUB_RUN_ATTEMPT', '1') != '1':
        print(json.dumps({
            'command': command,
            'exit_code': 0,
            'skipped': True,
            'reason': 'external command is idempotency-protected on workflow rerun',
        }, ensure_ascii=False))
        RESULT.write_text(json.dumps({
            'command': command,
            'exit_code': 0,
            'output': 'Skipped external side effect on workflow rerun.'
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        return 0
    proc = subprocess.run(COMMANDS[command], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=12*60)
    RESULT.write_text(json.dumps({'command':command,'exit_code':proc.returncode,'output':proc.stdout[-12000:]},ensure_ascii=False,indent=2),encoding='utf-8')
    print(proc.stdout)
    return proc.returncode
def report():
    result = json.loads(RESULT.read_text(encoding='utf-8')) if RESULT.exists() else {'exit_code':1,'output':'missing result'}
    print(json.dumps(result, ensure_ascii=False))
if __name__ == '__main__':
    mode = os.environ.get('CONTROL_MODE','execute')
    if mode == 'parse':
        raise SystemExit(parse())
    if mode == 'report':
        report()
    else:
        raise SystemExit(execute())
