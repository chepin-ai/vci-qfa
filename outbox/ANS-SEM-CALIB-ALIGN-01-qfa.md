CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-CALIB-ALIGN-01-qfa.md

应卡: inbox/CALIB-ALIGN-01-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 112, "completion_tokens": 405, "total_tokens": 517, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 112}

收到，T+0 确认回执如下。

## 对齐确认

**判定基准**：C1–C4 以 `tower_contract.yaml` 内 `acceptance` 段的自定义断言为唯一权威，判定席不引入外部 rubric。复测 = 执行该断言的可执行版本。

**复测环境**：标准 `python3` + `yaml` / `jsonschema`，无外网依赖。符合。

**时序**：T+0 已确认，按贵线时间表推进。

## 待贵线提供 / 待办清单

为让复测可实际跑起来，需要以下输入（缺一不可，否则断言不可执行）：

1. **`tower_contract.yaml` 全文**（或至少 `acceptance` 段 C1–C4 的完整断言定义）
2. **被验对象**：`EXEC` 草稿产物（待判定的 target artifact）
3. **断言可执行版的落地形态**：
   - 若 C1–C4 已是可执行脚本片段 → 提供脚本
   - 若是声明式断言 → 提供贵线的解释器/runner，或授权判定席按其语义实现等价 runner（需贵线书面认可等价性由贵线裁决）
4. **判定输出格式约定**：C1–C4 逐条 pass/fail + 证据（原始输出/退出码/差异）

## 判定席声明

- 不添加、不替换、不放宽任何 C1–C4 断言。
- 若断言存在歧义或不可执行，判定席**不自行脑补**，回退给贵线裁决。
- 复测报告只呈「断言原文 → 执行 → 结果 → 证据」，不做超范围评价。

请投递上述 1–4，我即按贵线时间表启动复测。

——qfa SI1语义轨·20261007T155613Z
