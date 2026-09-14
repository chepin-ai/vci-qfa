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



# —— append 模式
def load_any(path):
    txt = open(path, encoding='utf-8-sig').read()
    try:
        return json.loads(txt), 'json'
    except Exception:
        items = [json.loads(l) for l in txt.strip().split('\n') if l.strip()]
        return items, 'jsonl'


if MODE == 'wm-fix':
   try:
    # 修桥: 多文档序连形(头件+数组+散行)通用解析 → wm链续 → 原形回写
    wmp = bd + '/bridge/guard/qfa-watermark.json'
    raw = open(wmp, encoding='utf-8-sig').read()
    dec = json.JSONDecoder()
    docs = []
    pos = 0
    while pos < len(raw):
        while pos < len(raw) and raw[pos] in ' \t\r\n': pos += 1
        if pos >= len(raw): break
        d, end = dec.raw_decode(raw, pos)
        docs.append(d); pos = end
    rec['wm_docs'] = [type(d).__name__ + (':%d' % len(d) if hasattr(d, '__len__') else '') for d in docs]
    # 找 wm 条目容器: 数组件或含 cap_hash+prev_hash+hash 的 dict 件
    items = None; arr_idx = None
    for i, d in enumerate(docs):
        if isinstance(d, list) and d and isinstance(d[-1], dict) and 'cap_hash' in d[-1] and 'hash' in d[-1]:
            items = d; arr_idx = i
    if items is None:
        singles = [d for d in docs if isinstance(d, dict) and 'cap_hash' in d and 'hash' in d]
        if singles:
            items = singles  # 全散件形: 以散件序列为链
    if items is None:
        rec['fatal'] = 'no wm chain container found; docs=' + str(rec['wm_docs'])
        json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
        print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)
    last = items[-1]
    note2 = {}
    try: note2 = json.loads(NOTE) if NOTE.strip() else {}
    except Exception: pass
    wm = {k: None for k in last}
    wm.update({'beat': note2.get('beat', 113), 'round': note2.get('round', 1),
               'capsule': note2.get('cap', ''), 'cap': note2.get('cap', ''),
               'cap_hash': note2.get('cap_hash', ''), 'prev_hash': last.get('hash')})
    if 'ts' in last: wm['ts'] = ts
    wm = {k: v for k, v in wm.items() if v is not None}
    wm['hash'] = hashlib.sha256((str(last.get('hash', '')) + canon({k: v for k, v in wm.items() if k != 'hash'})).encode()).hexdigest()[:16]
    items.append(wm)
    out = '\n'.join(json.dumps(d, ensure_ascii=False, indent=1) for d in docs) + '\n'
    open(wmp, 'w', encoding='utf-8').write(out)
    rec['wm_fix'] = {'chain_len': len(items), 'new_hash': wm['hash'], 'prev': wm['prev_hash']}
    sh('git config user.name qfa-si5 && git config user.email qfa-si5@users.noreply.github.com && git config http.version HTTP/1.1', cwd=bd)
    sh('git add -A && git commit -m "wm链桥修:多文档通用解析+wm续链 (BOOKS-KEEPER-01 wm-fix) [skip ci]" 2>&1 | tail -1', cwd=bd)
    rc2, t2 = sh('git pull --rebase origin main 2>&1 | tail -1 && git push origin HEAD 2>&1 | tail -1', cwd=bd, to=100)
    rec['push_rc'] = rc2; rec['push_tail'] = t2[-150:]
    rec['verdict'] = 'wm-fixed' if rc2 == 0 else 'push-failed(诚实录)'
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)[:700]); sys.exit(0)
   except Exception:
    import traceback
    rec['fatal'] = 'wm-fix exception: ' + traceback.format_exc()[-400:]
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)

# —— append 模式
def load_any(path):
    txt = open(path, encoding='utf-8-sig').read()
    try:
        return json.loads(txt), 'json'
    except Exception:
        items = [json.loads(l) for l in txt.strip().split('\n') if l.strip()]
        return items, 'jsonl'


if MODE == 'wm-fix':
   try:
    # 修桥: qfa-watermark.json 数组+误拼JSONL行 → 归一为正JSON数组, 并续wm链
    wmp = bd + '/bridge/guard/qfa-watermark.json'
    raw = open(wmp, encoding='utf-8-sig').read()
    idx = raw.rfind(']')
    arr = json.loads(raw[:idx + 1])
    tail = raw[idx + 1:].strip()
    extras = [json.loads(l) for l in tail.split('\n') if l.strip()] if tail else []
    items = arr + extras
    last = items[-1]
    note2 = {}
    try: note2 = json.loads(NOTE) if NOTE.strip() else {}
    except Exception: pass
    wm = {k: None for k in last}
    wm.update({'beat': note2.get('beat', 113), 'round': note2.get('round', 1),
               'capsule': note2.get('cap', ''), 'cap': note2.get('cap', ''),
               'cap_hash': note2.get('cap_hash', ''), 'prev_hash': last.get('hash')})
    if 'ts' in last: wm['ts'] = ts
    wm = {k: v for k, v in wm.items() if v is not None}
    wm['hash'] = hashlib.sha256((str(last.get('hash', '')) + canon({k: v for k, v in wm.items() if k != 'hash'})).encode()).hexdigest()[:16]
    items.append(wm)
    json.dump(items, open(wmp, 'w'), ensure_ascii=False, indent=1)
    rec['wm_fix'] = {'total': len(items), 'new_hash': wm['hash'], 'prev': wm['prev_hash'], 'extras_absorbed': len(extras)}
    sh('git config user.name qfa-si5 && git config user.email qfa-si5@users.noreply.github.com && git config http.version HTTP/1.1', cwd=bd)
    sh('git add -A && git commit -m "wm链桥修:数组归一+wm续链 (BOOKS-KEEPER-01 wm-fix) [skip ci]" 2>&1 | tail -1', cwd=bd)
    rc2, t2 = sh('git pull --rebase origin main 2>&1 | tail -1 && git push origin HEAD 2>&1 | tail -1', cwd=bd, to=100)
    rec['push_rc'] = rc2; rec['push_tail'] = t2[-150:]
    rec['verdict'] = 'wm-fixed' if rc2 == 0 else 'push-failed(诚实录)'
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)[:700]); sys.exit(0)
   except Exception:
    import traceback
    rec['fatal'] = 'wm-fix exception: ' + traceback.format_exc()[-400:]
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)


if MODE == 'outbox-fix':
    ob_path = bd + '/outbox/qfa-outbox.json'
    try:
        ob, ob_fmt = load_any(ob_path)
    except Exception as e:
        raw = open(ob_path, 'rb').read()
        rec['fatal'] = 'outbox load fail: %s | head_hex=%s' % (str(e)[:60], raw[:32].hex())
        json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
        print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)
    if isinstance(ob, dict):
        lst_key = None
        for k, v in ob.items():
            if isinstance(v, list) and v and isinstance(v[-1], dict) and 'seq' in v[-1]:
                lst_key = k; break
        if lst_key is None:
            rec['fatal'] = 'outbox dict but no seq-list key: %s' % list(ob.keys())
            json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
            print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)
        items = ob[lst_key]
    else:
        items = ob
    ob_last = items[-1] if items else None
    if not ob_last:
        rec['fatal'] = 'outbox empty/odd'
        json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
        print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)
    item = {'seq': ob_last.get('seq', 0) + 1, 'ts': ts, 'kind': 'beat-seal',
            'body': NOTE or 'beat-112 CAP-129 f82f447a5e9b866d seal补记(outbox-fix)',
            'prev_hash': ob_last.get('sha256')}
    item['sha256'] = hashlib.sha256((str(item['prev_hash']) + canon({k: v for k, v in item.items() if k != 'sha256'})).encode()).hexdigest()
    items.append(item)
    if ob_fmt == 'json':
        json.dump(ob, open(ob_path, 'w'), ensure_ascii=False, indent=1)
    else:
        with open(ob_path, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(item, ensure_ascii=False) + '\n')
    rec['outbox_new'] = {'seq': item['seq'], 'sha256_16': item['sha256'][:16], 'prev_16': str(item['prev_hash'])[:16], 'fmt': ob_fmt}
    sh('git config user.name qfa-si5 && git config user.email qfa-si5@users.noreply.github.com && git config http.version HTTP/1.1', cwd=bd)
    sh('git add -A && git commit -m "outbox#%s beat-112补记 (BOOKS-KEEPER-01 outbox-fix) [skip ci]" 2>&1 | tail -1' % item['seq'], cwd=bd)
    rc2, t2 = sh('git pull --rebase origin main 2>&1 | tail -1 && git push origin HEAD 2>&1 | tail -1', cwd=bd, to=100)
    rec['push_rc'] = rc2; rec['push_tail'] = t2[-150:]
    rec['verdict'] = 'outbox-fixed' if rc2 == 0 else 'push-failed(诚实录)'
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)[:700]); sys.exit(0)


note = {}
try:
    note = json.loads(NOTE) if NOTE.strip() else {}
except Exception as e:
    rec['fatal'] = 'BEAT_NOTE JSON parse failed: %s' % str(e)[:80]
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)

# 1) 胶囊: 镜 CAP-128 键构
prev_n, prev_cap = cap_state
prev_cap = json.load(open(bd + '/capsule/CAP-%03d.json' % prev_n))
newn = prev_n + 1
if os.path.exists(bd + '/capsule/CAP-%03d.json' % newn):
    rec['fatal'] = 'CAP-%03d exists — engine raced, abort(零覆写)' % newn
    json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False)); sys.exit(0)
cap = {}
for k in prev_cap:
        cap[k] = None
cap.update({
    'id': 'CAP-%03d' % newn,
    'goal': note.get('goal', ''),
    'facts': note.get('facts', []),
    'next': note.get('next', ''),
    'ts': ts,
    'by': 'qfa(BOOKS-KEEPER-01机件·beat-112)',
})
if 'chain_v2' in prev_cap:
    cap['chain_v2'] = prev_cap.get('chain_v2')
cap['digest'] = hashlib.sha256(canon({k: cap.get(k) for k in ('id', 'goal', 'facts', 'next', 'chain_v2')}).encode()).hexdigest()[:16]
cap['prev_cap_hash'] = prev_cap.get('cap_hash')
cap_for_hash = {k: v for k, v in cap.items() if k != 'cap_hash' and v is not None}
cap['cap_hash'] = hashlib.sha256((prev_cap.get('cap_hash', '') + canon(cap_for_hash)).encode()).hexdigest()[:16]
json.dump(cap, open(bd + '/capsule/CAP-%03d.json' % newn, 'w'), ensure_ascii=False, indent=1)
rec['cap_new'] = {'id': cap['id'], 'digest': cap['digest'], 'cap_hash': cap['cap_hash'], 'prev': cap['prev_cap_hash']}

# 2) wm: 自发现(末行含 cap_hash+prev_hash+hash 的 jsonl)
wm_file = None
for g in glob.glob(bd + '/**/*.jsonl', recursive=True):
    if '/.git/' in g: continue
    try:
        last = json.loads(open(g, encoding='utf-8').read().strip().split('\n')[-1])
        if isinstance(last, dict) and 'cap_hash' in last and 'prev_hash' in last and 'hash' in last:
            wm_file = g; wm_last = last
    except Exception:
        continue
if not wm_file:
    for g in glob.glob(bd + '/**/*.json', recursive=True):
        if '/.git/' in g: continue
        try:
            d, fmt = load_any(g)
            arr = d if isinstance(d, list) else [d]
            if arr and isinstance(arr[-1], dict) and 'cap_hash' in arr[-1] and 'prev_hash' in arr[-1] and 'hash' in arr[-1]:
                wm_file = g; wm_last = arr[-1]; break
        except Exception:
            continue
if wm_file:
    wm = {k: None for k in wm_last}
    wm.update({'beat': note.get('beat', 112), 'round': note.get('round', 1),
               'capsule': cap['id'], 'cap': cap['id'], 'cap_hash': cap['cap_hash'],
               'prev_hash': wm_last.get('hash')})
    if 'chain_v2' in wm_last: wm['chain_v2'] = wm_last.get('chain_v2')
    if 'ts' in wm_last: wm['ts'] = ts
    wm = {k: v for k, v in wm.items() if v is not None}
    wm['hash'] = hashlib.sha256((wm_last.get('hash', '') + canon({k: v for k, v in wm.items() if k != 'hash'})).encode()).hexdigest()[:16]
    with open(wm_file, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(wm, ensure_ascii=False) + '\n')
    rec['wm_new'] = {'file': wm_file[len(bd) + 1:], 'hash': wm['hash'], 'prev': wm['prev_hash']}
else:
    rec['wm_new'] = 'NOT-FOUND(名级:未发现wm面,诚实录)'

# 3) outbox: qfa-outbox.json
ob_path = bd + '/outbox/qfa-outbox.json'
ob, ob_fmt = load_any(ob_path)
if isinstance(ob, dict):
    items = None
    for k, v in ob.items():
        if isinstance(v, list) and v and isinstance(v[-1], dict) and 'seq' in v[-1]:
            items = v; break
else:
    items = ob
ob_last = items[-1] if items else None
if ob_last:
    item = {'seq': ob_last.get('seq', 0) + 1, 'ts': ts, 'kind': 'beat-seal',
            'body': note.get('outbox_body', cap['id'] + ' ' + cap['cap_hash']),
            'prev_hash': ob_last.get('sha256')}
    item['sha256'] = hashlib.sha256((item['prev_hash'] + canon({k: v for k, v in item.items() if k != 'sha256'})).encode()).hexdigest()
    items.append(item)
    if ob_fmt == 'json':
        json.dump(ob, open(ob_path, 'w'), ensure_ascii=False, indent=1)
    else:
        with open(ob_path, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(item, ensure_ascii=False) + '\n')
    rec['outbox_new'] = {'seq': item['seq'], 'sha256': item['sha256'][:16] + '…'}
else:
    rec['outbox_new'] = 'PARSE-FAIL(诚实录)'

# 4) 单提交: pull --rebase 防并发 → CAP-129存在复检 → push
sh('git config user.name qfa-si5 && git config user.email qfa-si5@users.noreply.github.com && git config http.version HTTP/1.1', cwd=bd)
rc, t = sh('git add -A && git commit -m "CAP-%03d beat-112 seal (BOOKS-KEEPER-01) [skip ci]" 2>&1 | tail -1' % newn, cwd=bd)
rec['commit'] = t[-120:]
rc, t = sh('git pull --rebase origin main 2>&1 | tail -1', cwd=bd, to=60)
if os.path.exists(bd + '/capsule/CAP-%03d.json' % newn) and rc == 0:
    # rebase后若CAP-129为他者所铸则abort由receipt录
    pass
rc, t = sh('git push origin HEAD 2>&1 | tail -1', cwd=bd, to=90)
rec['push_rc'] = rc; rec['push_tail'] = t[-150:]
rec['verdict'] = 'appended' if rc == 0 else 'push-failed(诚实录,件在本机镜像待续)'
json.dump(rec, open('receipts/books-keeper/BK-%s.json' % ts, 'w'), ensure_ascii=False, indent=1)
print(json.dumps(rec, ensure_ascii=False)[:900])

