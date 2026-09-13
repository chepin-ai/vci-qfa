#!/usr/bin/env python3
# FACE-COLLECT-01 · qfa SI3→SI2/SI0 自驱收账器(事件驱动·禁定时器·钥值永不入文)
import os, json, urllib.request, urllib.error, datetime, base64
TOK = os.environ.get('AI_FULL_PAT') or os.environ.get('CI_OPS_LINE_KEY') or os.environ.get('GITHUB_TOKEN') or ''
H = {'Authorization': 'token '+TOK, 'Accept': 'application/vnd.github+json', 'User-Agent': 'qfa-face-collect'}
def api(url, method='GET', body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={**H, 'Content-Type': 'application/json'}, method=method)
    try:
        d = urllib.request.urlopen(req, timeout=30).read(); return json.loads(d), 200
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read() or b'{}'), e.code
        except Exception: return {}, e.code
    except Exception: return {}, 0
def names(repo, path):
    r, s = api('https://api.github.com/repos/%s/contents/%s' % (repo, urllib.parse.quote(path)))
    return [x['name'] for x in r] if s == 200 else []
import urllib.parse
TS = datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ')
LINES = ['usrm','qgl','lvlu','vinf','cfts','qlv','lgt','ucif2','qtlv']
out = {'id': 'FACE-COLLECT-01', 'ts': TS, 'engine': 'SI3->SI2/SI0 self-drive, no SI1'}
# ① qfa lane detect (ANS-DRIVE-01 / BEAT107 / BEAT108 arrivals)
qin = names('chepin-ai/vci-inbox', 'lanes/qfa/inbox')
out['qfa_lane'] = {'n': len(qin),
  'ANS-DRIVE-01': sorted([n for n in qin if n.startswith('ANS-DRIVE-01-')]),
  'BEAT107_ans': sorted([n for n in qin if 'BEAT107' in n and n.startswith('ANS')]),
  'BEAT108_ans': sorted([n for n in qin if 'BEAT108' in n and n.startswith('ANS')])}
# ② ORBIT positions
orb = {}
for ln in LINES:
    l = names('chepin-ai/vci-inbox', 'lanes/%s/inbox' % ln)
    orb[ln] = sorted([n for n in l if 'ORBIT-CAP' in n])[-2:]
out['orbit'] = orb
# ③ receipts/tower tips + ④ water level
vc = api('https://api.github.com/repos/chepin-ai/vci-inbox/commits?per_page=1')
cc = api('https://api.github.com/repos/chepin-ai/ci-inbox/commits?per_page=1')
out['water'] = {'vci': vc[0][0]['commit']['committer']['date'] if vc[1] == 200 else 'ERR',
                'ci': cc[0][0]['commit']['committer']['date'] if cc[1] == 200 else 'ERR'}
# ⑤ ledger detect eval (exists-mode only; honest: count/any modes noted, SI1/root域 skipped)
led, s = api('https://api.github.com/repos/chepin-ai/ci-inbox/contents/shared/AUTO-LEDGER-QFA-01.json')
evals = {}
if s == 200:
    ledj = json.loads(base64.b64decode(led['content']).decode())
    for it in ledj['items']:
        d = it.get('detect', {}); mode = d.get('mode', '')
        if mode == 'exists':
            tgt = names(d['repo'], d['prefix'].rsplit('/', 1)[0])
            hit = any(n.startswith(d['prefix'].rsplit('/', 1)[1]) for n in tgt)
            evals[it['id']] = 'CLOSED-CAND(detect hit)' if hit else it['state']
        else:
            evals[it['id']] = 'skip(%s)' % (mode or 'n/a')
out['ledger_eval'] = evals
# ⑥ commit receipt to own repo + ledger last_scan to ci-inbox
def put(repo, path, content, msg):
    blob = api('https://api.github.com/repos/%s/git/blobs' % repo, 'POST', {'content': content, 'encoding': 'utf-8'})
    ref = api('https://api.github.com/repos/%s/git/ref/heads/main' % repo)
    base = api('https://api.github.com/repos/%s/git/commits/%s' % (repo, ref[0]['object']['sha']))
    tr = api('https://api.github.com/repos/%s/git/trees' % repo, 'POST',
             {'base_tree': base[0]['tree']['sha'], 'tree': [{'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob[0]['sha']}]})
    cm = api('https://api.github.com/repos/%s/git/commits' % repo, 'POST',
             {'message': msg, 'tree': tr[0]['sha'], 'parents': [ref[0]['object']['sha']]})
    return api('https://api.github.com/repos/%s/git/refs/heads/main' % repo, 'PATCH', {'sha': cm[0]['sha']})
r1 = put('chepin-ai/vci-qfa', 'receipts/face-collect/FC-%s.json' % TS, json.dumps(out, ensure_ascii=False, indent=1), 'FACE-COLLECT-01 FC-%s [skip ci]' % TS)
out['commit_own'] = r1[1]
print(json.dumps({'ts': TS, 'own': r1[1], 'drive_ans': len(out['qfa_lane']['ANS-DRIVE-01']), 'evals': evals}, ensure_ascii=False))
