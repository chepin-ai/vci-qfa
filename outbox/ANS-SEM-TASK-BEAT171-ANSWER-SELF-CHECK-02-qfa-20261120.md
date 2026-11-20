CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-TASK-BEAT171-ANSWER-SELF-CHECK-02-qfa-20261120.md

应卡: inbox/TASK-BEAT171-ANSWER-SELF-CHECK-02-qfa-20261120.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 73, "completion_tokens": 961, "total_tokens": 1034, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 73}

我先说明：当前对话里没有挂载任何仓库、文件系统或工具执行环境，我无法真正读取 `outbox/`、拿到 commit SHA、run id、artifact 或计算 SHA256。因此我不能伪造"已执行"的回卡。下面给出可执行的补证方案与回卡模板；其中所有 `<>` 占位必须由你在有仓库访问的环境里填入真实值后才能生效。

## 一、固定 commit 与真实 run 的绑定方式

- 固定 commit：`git rev-parse HEAD` 输出记为 `<COMMIT_SHA>`；同时记录 `git status --porcelain` 为空，证明工作树干净。
- 真实 run：取 CI/本地执行产生的 run 标识 `<RUN_ID>`（如 GitHub Actions 的 `run_id` / 本地 `run-<timestamp>-<short sha>`）。
- 绑定断言：run 的元数据里必须含 `commit=<COMMIT_SHA>`，否则不算真实 run 补证。

## 二、命令（在仓库根执行）

```bash
set -euo pipefail
COMMIT_SHA=$(git rev-parse HEAD)
test -z "$(git status --porcelain)" || { echo "dirty tree"; exit 1; }
RUN_ID="${RUN_ID:?set RUN_ID}"
OUT="outbox/ANS-BEAT171-ANSWER-SELF-CHECK-02-qfa"
mkdir -p "$OUT"

# 1) 生成真实 run 清单（示例：把自评完成度挂到实际产物上）
python tools/qfa_selfcheck.py \
  --commit "$COMMIT_SHA" \
  --run-id "$RUN_ID" \
  --emit-manifest "$OUT/run-manifest.json"

# 2) 盲重放（不带自评/期望值，只重跑产物生成）
python tools/qfa_replay.py \
  --manifest "$OUT/run-manifest.json" \
  --blind \
  --out "$OUT/replay"

# 3) 计算 artifact SHA256
sha256sum "$OUT"/replay/artifact.* > "$OUT/artifact.sha256"
```

> 若仓库里脚本名不同，替换 `tools/qfa_selfcheck.py` / `tools/qfa_replay.py` 为实际入口；关键是三件事：commit 固化、盲重放不含期望值、SHA256 落盘。

## 三、正负控与独立重放

- 正控：用已知通过的样例 `<POS_FIXTURE>` 跑同一管线，期望 `exit 0` 且 SHA256 与 `<POS_EXPECTED_SHA>` 一致。
- 负控：篡改一个字节（如 `printf 'x' >> artifact`）后重算 SHA256，期望与清单不一致并返回非零。
- 独立重放：在另一干净 checkout（同 `<COMMIT_SHA>`）用不同 `RUN_ID` 重跑盲重放，比较两份 `artifact.sha256` 是否逐行一致；一致才记为独立重放通过。

## 四、回卡（填入真实值后提交到 outbox）

```markdown
# ANS-BEAT171-ANSWER-SELF-CHECK-02-qfa 回卡

- commit: <COMMIT_SHA>（工作树干净）
- run: <RUN_ID>（元数据 commit 匹配）
- artifact: <ARTIFACT_PATH>
- sha256: <ARTIFACT_SHA256>
- 命令: 见 run-manifest.json 中 commands[] 字段
- 正控: <POS_FIXTURE> -> exit 0, sha256=<POS_EXPECTED_SHA> ✔
- 负控: 单字节篡改 -> sha256 不匹配, exit!=0 ✔
- 盲重放: blind=true, 不含期望值, 产物 sha256 与主 run 一致 ✔
- 独立重放: 干净 checkout@<COMMIT_SHA>, run=<RUN2_ID>, sha256 逐行一致 ✔
- 自评完成度: <X>/<Y>，挂接字段 run-manifest.json#self_assessment
```

需要我现在做的话，请把仓库以可访问方式提供（或粘贴 `tools/` 下相关脚本与一次 run 的日志），我就能按上面流程实际执行并把真实 SHA256、run id、正负控结果填进回卡；在此之前，我不会声称已完成补证。

——qfa SI1语义轨·20261120T052027Z
