#!/usr/bin/env python3
# QFA-TOWER-01 — qfa线SI0塔（塔范式·轻量版）
# 五律: 零定时器 / 自级联 / 防自激 / 钥在仓 / 拍尾生债
import os, json, time, base64, urllib.request, datetime, subprocess, sys, re

REPO = os.environ.get('GITHUB_REPOSITORY', 'chepin-ai/vci-qfa')
TOK_W = os.environ.get('GITHUB_TOKEN')
TOK_R = os.environ.get('LINE_PAT') or TOK_W
HUB = 'chepin-ai/vci-inbox'
LINE = 'qfa'

def api(method, path, data=None, repo=None, write=False):
    url = f'https://api.github.com/repos/{repo or REPO}/{path}'
    tok = TOK_W if (write or (repo or REPO) == REPO and method in ('PUT','POST','DELETE')) else TOK_R
    if path == 'dispatches' and os.environ.get('LINE_PAT'):
        tok = os.environ.get('LINE_PAT')
    req = urllib.request.Request(url, method=method,
        headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'qfa-tower'})
    if data is not None:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {'err': f'{e.__class__.__name__}: {e}'}

def get_file(remote, repo=None):
    st, j = api('GET', 'contents/' + remote, repo=repo)
    if st != 200: return None, None
    return base64.b64decode(j['content']).decode(), j['sha']

def put_file(remote, text, sha, msg, repo=None):
    body = {'message': msg, 'content': base64.b64encode(text.encode()).decode()}
    if sha: body['sha'] = sha
    for _ in range(5):
        st, j = api('PUT', 'contents/' + remote, body, repo=repo, write=True)
        if st in (200, 201): return True
        time.sleep(2)
    return False

def patrol():
    events = []
    # Scan hub board for qfa-related items
    st, items = api('GET', 'contents/公告板', repo=HUB)
    if st == 200:
        names = sorted((i['name'] for i in items if i['name'].endswith('.md')), key=lambda n: n)[-12:]
        for n in names:
            if LINE in n.lower():
                events.append({'kind': 'hub-board', 'ref': n})
            elif re.search(r'OTP@all|OTP@qfa|\u3010S-I|军令|奉\s*root', n, re.I):
                events.append({'kind': 'hub-broadcast', 'ref': n})
    # Scan own inbox
    st, items = api('GET', 'contents/inbox')
    if st == 200:
        for i in items[-8:]:
            if i['name'] != '.gitkeep':
                events.append({'kind': 'inbox', 'ref': i['name']})
    return events

def write_receipt(events, verdict='patrol-ok'):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    receipt = {
        'v': 'QFA-TOWER-01',
        'ts': ts,
        'events': events if events else [{'kind': 'patrol', 'ref': 'qfa-autonomy-02'}],
        'verdict': verdict,
        'repo': REPO
    }
    remote = f'receipts/tower/QT-{ts.replace(":","")}.json'
    text = json.dumps(receipt, ensure_ascii=False, indent=2)
    old, sha = get_file(remote)
    if old is not None:
        try:
            old_data = json.loads(old)
            old_data['events'].extend(events)
            old_data['verdict'] = verdict
            text = json.dumps(old_data, ensure_ascii=False, indent=2)
        except:
            pass
    ok = put_file(remote, text, sha, f'qfa receipt {ts}')
    if not ok:
        os.makedirs('receipts/tower', exist_ok=True)
        with open(remote.replace('/', os.sep), 'w') as f:
            f.write(text)
        subprocess.run(['git', 'config', 'user.name', 'qfa-tower'], capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'qfa@chepin.ai'], capture_output=True)
        subprocess.run(['git', 'add', '-A'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'qfa receipt {ts}', '-q'], capture_output=True)
        for i in range(3):
            r1 = subprocess.run(['git', 'pull', '--rebase', '-q'], capture_output=True)
            r2 = subprocess.run(['git', 'push', '-q'], capture_output=True)
            if r2.returncode == 0:
                break
            time.sleep(2 + i * 2)
    return remote, receipt

def self_cascade():
    events = patrol()
    if len(events) > 0:
        st, _ = api('POST', 'dispatches', {
            'event_type': 'qfa-wake',
            'client_payload': {'src': 'qfa-tower', 'kind': 'self-cascade', 'pending': len(events)}
        })
        print(f'self-cascade dispatch: status={st}')
    return events

def mesh_wake():
    hub_pat = os.environ.get('LINE_PAT')
    if not hub_pat:
        print('mesh-wake: no LINE_PAT, skip')
        return
    req = urllib.request.Request(
        'https://api.github.com/repos/chepin-ai/ci-worker-01/dispatches',
        method='POST',
        headers={'Authorization': f'token {hub_pat}', 'Accept': 'application/vnd.github+json'},
        data=json.dumps({
            'event_type': 'federation-event',
            'client_payload': {'src': 'qfa-tower', 'kind': 'mesh-wake', 'sha': os.environ.get('GITHUB_SHA', '')}
        }).encode())
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f'mesh-wake: http={r.status}')
    except Exception as e:
        print(f'mesh-wake: err={e}')

if __name__ == '__main__':
    print(f'QFA-TOWER-01 starting at {datetime.datetime.now(datetime.timezone.utc).isoformat()}')
    events = patrol()
    print(f'patrol found {len(events)} events')
    remote, receipt = write_receipt(events)
    print(f'receipt written to {remote}')
    self_cascade()
    mesh_wake()
    print('QFA-TOWER-01 done')
