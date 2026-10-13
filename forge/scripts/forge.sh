#!/usr/bin/env bash
set -euo pipefail
REPO=chepin-qi/qfa-os
TS=$(date -u +%Y%m%dT%H%M%SZ)
LOGDIR="$GITHUB_WORKSPACE/receipts/forge-qfos/logs"
mkdir -p "$LOGDIR"
# ERRATA-PROCESS-03: runner python3 is bare; engine verifiers need numpy. Conditional install.
python3 -c 'import numpy' 2>/dev/null || python3 -m pip install --quiet numpy
code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: token $QI" "https://api.github.com/repos/$REPO")
created=false
if [ "$code" = "404" ]; then
  curl -s -X POST -H "Authorization: token $QI" -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos -d '{"name":"qfa-os","private":true,"description":"QF-OS qfa line residence"}' > /tmp/create.json
  created=true
  sleep 3
elif [ "$code" != "200" ]; then
  echo "repo check failed: $code"; exit 1
fi
rm -rf /tmp/qfaos
if git clone --depth 1 "https://x-access-token:${QI}@github.com/${REPO}.git" /tmp/qfaos 2>/tmp/clone.err; then
  cd /tmp/qfaos
else
  mkdir -p /tmp/qfaos && cd /tmp/qfaos && git init -b main .
  git remote add origin "https://x-access-token:${QI}@github.com/${REPO}.git"
fi
git config user.name qfa-forge && git config user.email qfa-forge@local
rsync -a --delete --exclude .git "$GITHUB_WORKSPACE/forge/qfa-os/" .
cd engine/bound-proof
echo '{}' > /tmp/vres.json
for v in verify_bound*.py; do
  if python3 "$v" > "$LOGDIR/${TS}_${v}.log" 2>&1; then st=0; else st=$?; fi
  python3 "$GITHUB_WORKSPACE/forge/scripts/collect_vres.py" "$v" "$st"
done
cd /tmp/qfaos
git add -A
if git diff --cached --quiet; then changed=false; else
  git commit -m "forge-qfos-01 ${MODE} beat-127 [skip ci]" > /dev/null; changed=true
fi
if [ "$created" = "true" ] || [ "$changed" = "true" ]; then
  git push origin HEAD:main 2>/tmp/push.err || git push -u origin HEAD:main
fi
tip=$(git rev-parse HEAD)
cd "$GITHUB_WORKSPACE"
python3 forge/scripts/make_receipt.py "$TS" "$MODE" "$created" "$changed" "$tip"
git config user.name qfa-forge && git config user.email qfa-forge@local
git add receipts/forge-qfos
git commit -m "forge-qfos receipt $TS [skip ci]" > /dev/null
git push
