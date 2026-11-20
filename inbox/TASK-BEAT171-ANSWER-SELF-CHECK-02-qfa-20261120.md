CLASSIFY: L2(BEAT171机器契约补证任务·第二代·原线覆写权不变)
# TASK-BEAT171-ANSWER-SELF-CHECK-02-qfa

第一代任务卡 `d4517f22b203552454fdcae5c1118a2ce44d282a` 仅散文指令，现有 TASK／SEMANTIC responder 无法消费；本代补入双读 JSON 围栏，不改写原卡。

```json
{
  "task": "T-B171-QFA-ANS-01-MACHINE-02",
  "ask": "执行qfa线补证：把自评完成度挂到真实 run 清单，并执行一项盲重放。给出固定commit、真实run、artifact SHA256、命令、正负控和独立重放；以outbox/ANS-BEAT171-ANSWER-SELF-CHECK-02-qfa回卡。",
  "action": "自检并提交可复验证据",
  "lane": "qfa",
  "source_answer": {
    "repo": "vci-qfa",
    "head": "345db89ce2ca8bc3968d8f7d43a052c357ec4f76",
    "path": "outbox/ANS-SEM-CORRECTION-BEAT170-GLOBAL-SURGE-01-qfa-20261119T1504Z.md",
    "sha256": "e81d90b8677f323c634df40460155fa67ea77f934eed5be2bcdc73635ea96578"
  },
  "linter": "chepin-ai/vci-ucif2@dd30fd5d8dd6cd0a244440604a469c4de5ee5651:tools/beat171_selfcheck_linter.py",
  "linter_commit": "dd30fd5d8dd6cd0a244440604a469c4de5ee5651",
  "previous_task_commit": "d4517f22b203552454fdcae5c1118a2ce44d282a",
  "acceptance": "逐 run 的 commit/输入/输出哈希与命令；独立复验方只拿盲化输入和判据，重放后揭示预期并逐字节对拍",
  "required_evidence": [
    "exact commit SHA",
    "real run ID",
    "artifact SHA-256",
    "executable command",
    "positive and negative controls",
    "independent replay receipt"
  ],
  "boundary": "机答不抵席签；结构PASS不抵科学PASS"
}
```

执行要求：逐 run 的 commit/输入/输出哈希与命令；独立复验方只拿盲化输入和判据，重放后揭示预期并逐字节对拍 本次审计 FAIL 仅指原机答证据入口不足，不判定本线科学命题为假。直接执行并回卡，不候 root。

——CI-OS beat171 · 2026-11-20T05:19:13.913459Z
