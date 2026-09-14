#!/usr/bin/env python3
# books_keeper.py — BOOKS-KEEPER-01 机件:qfa-quantum-lab 账册续链(capsule/wm/outbox)
# 律: 值永不入文/日志(钥唯Actions注入内存); 未实测言未实测; 单次提交零重试; 布局不明=只侦察不写入
import json, os, re, subprocess, sys, time, hashlib, glob

def sh(c, cwd=None, to=90):
    r = subprocess.run(c, shell=True, cwd=cwd, capture_output=True, text=True, timeout=to)
    return r.returncode, (r.stdout + r.stderr)[-1500:]

def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

TOK = os.environ.get('GH_PAT_QI_FULL', '')
MODE = os.environ.get('MODE', 'recon')
NOTE = os.environ.get('BEAT_NOTE', '')
ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
os.makedirs('receipts/books-keeper', exist_ok=True)
rec = {'id': 'BOOKS-KEEPER-01', 'ts': ts, 'mode': MODE, 'clock': 'VOID'}

if not TOK:
    rec['fatal'] = 'GH_PAT_QI_FULL absent'
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec)); sys.exit(0)

bd = '/tmp/books'
subprocess.run('rm -rf ' + bd, shell=True)
rc, t = sh('git clone --depth 60 https://x-access-token:%s@github.com/chepin-qi/qfa-quantum-lab.git %s 2>&1 | tail -2' % (TOK, bd), to=110)
rec['clone_rc'] = rc
if rc != 0:
    rec['fatal'] = 'clone failed (scope? %s)' % t[-120:]
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)

# —— 布局侦察(名级):  capsules / wm / outbox 候选面
layout = {}
caps = []
for g in glob.glob(bd + '/**/*.json', recursive=True) + glob.glob(bd + '/**/*.jsonl', recursive=True):
    rel = g[len(bd) + 1:]
    if '/.git/' in g: continue
    base = os.path.basename(g)
    if re.search(r'cap|CAP', base): caps.append(rel)
    elif re.search(r'wm|chain', base.lower()): layout.setdefault('wm_cand', []).append(rel)
    elif re.search(r'outbox', base.lower()): layout.setdefault('outbox_cand', []).append(rel)
layout['cap_cand'] = caps[:10]
rec['layout'] = layout

# 定胶囊最新态: 扫 cap_cand 中 CAP-序最大者
cap_state = None
cap_file = None
for rel in caps:
    try:
        d = json.load(open(bd + '/' + rel))
    except Exception:
        continue
    items = d if isinstance(d, list) else ([d] if isinstance(d, dict) else [])
    for it in items:
        if isinstance(it, dict) and re.match(r'CAP-\d+', str(it.get('id', ''))):
            n = int(it['id'].split('-')[1])
            if cap_state is None or n > cap_state[0]:
                cap_state = (n, it); cap_file = rel
if cap_state:
    rec['cap_latest'] = {'n': cap_state[0], 'file': cap_file,
                         'cap_hash': cap_state[1].get('cap_hash'),
                         'prev_cap_hash': cap_state[1].get('prev_cap_hash')}
# wm/outbox 最新行
for key in ('wm_cand', 'outbox_cand'):
    for rel in layout.get(key, []):
        try:
            lines = open(bd + '/' + rel, encoding='utf-8').read().strip().split('\n')
            last = json.loads(lines[-1])
            rec.setdefault('tails', {})[rel] = {k: last.get(k) for k in ('id', 'beat', 'hash', 'sha256', 'seq') if k in last}
        except Exception as e:
            rec.setdefault('tails', {})[rel] = 'unparsed: %s' % str(e)[:60]

if MODE == 'recon':
    rec['verdict'] = 'recon-only: 布局在案,未写任何件'
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)[:800]); sys.exit(0)

# —— append 模式: 唯布局无歧义方写
rec['verdict'] = 'append-mode: 布局歧义守(本版先recon,append逻辑候qfa SI1按receipt核准)'
json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
print(json.dumps(rec, ensure_ascii=False)[:800])
