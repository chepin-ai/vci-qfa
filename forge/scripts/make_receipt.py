import json, os, sys
ts, mode, created, changed, tip = sys.argv[1:6]
vres = json.load(open('/tmp/vres.json')) if os.path.exists('/tmp/vres.json') else {}
try:
    note = json.loads(os.environ.get('NOTE', '{}') or '{}')
except Exception:
    note = {'_raw': os.environ.get('NOTE', '')[:200]}
rec = {"id": "FORGE-QFOS-01", "ts": ts, "mode": mode, "repo": "chepin-qi/qfa-os", "private": True,
       "created": created == "true", "changed": changed == "true", "tip": tip,
       "engine_selftest": vres,
       "engine_selftest_pass": (all(v == 0 for v in vres.values()) if vres else None),
       "note": note}
path = f"receipts/forge-qfos/FQ-{ts}.json"
os.makedirs('receipts/forge-qfos', exist_ok=True)
json.dump(rec, open(path, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
print(path)
