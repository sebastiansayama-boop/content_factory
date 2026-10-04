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
    'telegram-test': ['python','-m','pytest','-s','-q','tests/test_telegram_publication_smoke.py::test_real_telegram_publication_media_smoke','tests/test_telegram_historical_material_smoke.py','-m','external'],
    'publication-test': ['python','-m','pytest','-q','tests/test_provider_e2e.py::test_live_historical_publication_text_variations_without_images','-m','external'],
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
    command = os.environ['CONTROL_COMMAND']
    proc = subprocess.run(COMMANDS[command], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=12*60)
    RESULT.write_text(json.dumps({'command':command,'exit_code':proc.returncode,'output':proc.stdout[-12000:]},ensure_ascii=False,indent=2),encoding='utf-8')
    print(proc.stdout)
    return proc.returncode
def report():
    result = json.loads(RESULT.read_text(encoding='utf-8')) if RESULT.exists() else {}
    command = os.environ.get('COMMAND', result.get('command','unknown'))
    status = os.environ.get('COMMAND_STATUS','unknown')
    output = result.get('output','No execution output.')
    issue = os.environ['ISSUE_NUMBER']; repo = os.environ['REPO']
    body = '## Control Plane\n\nCommand: '+command+'\nGitHub job: '+status+'\nRevision: '+subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()+'\n\n### Result\n\n```text\n'+output[-10000:]+'\n```'
    import urllib.request
    req = urllib.request.Request('https://api.github.com/repos/'+repo+'/issues/'+issue+'/comments', data=json.dumps({'body':body}).encode(), method='POST', headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','Content-Type':'application/json','X-GitHub-Api-Version':'2022-11-28'})
    with urllib.request.urlopen(req,timeout=30): pass
    return 0
if __name__ == '__main__': raise SystemExit({'parse':parse,'execute':execute,'report':report}[sys.argv[1]]())