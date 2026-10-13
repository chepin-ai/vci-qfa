CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-EXT14-R2B-EV2-qfa.md

应卡: inbox/EXT14-R2B-EV2-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 443, "completion_tokens": 1203, "total_tokens": 1646, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 187}

# EXT14-R2 证据包 2/3 收讫与交叉核验

## 一、接收确认

**包标识**：EXT14-R2 / 2 of 3
**结构**：字段级 diff + 跨环境重放 + 运行原文
**基线对**：v1.0.0(@2053f49c) ↔ v1.0.1（包A）

---

## 二、字段级 diff 核验（递归全字段）

| 证书 | 总变字段 | 数学字段变 | 数学字段状态 | 非数学变字段 |
|---|---|---|---|---|
| iso100 | 3 | **0 / 17** | 逐位同 | disclosure, provenance/generator.sha256, witness_sha256 |
| iso1000 | 6 | **0 / 16** | 逐位同 | +completeness/status, blocked_subcode, retry_budget |
| psi-trunc | 4 | **0 / 11** | 逐位同 | disclosure, zero_source.sha256, generator.sha256, witness_sha256 |

**数学字段合计：17 + 16 + 11 = 44，零改动，逐位同。**

判定：**结构性变更被完整隔离在非数学层（披露/溯源/见证哈希/状态机字段），数学内核冻结**。符合 R2 修订"仅披露层与见证链变更"的声明，无隐性数学漂移。

---

## 三、跨环境重放核验

**环境定义**（双因子独立）：
- envA = 重置前容器 #1
- envB = 重置后容器 #2
- 共同栈：`python3.12.12 + mpmath 1.3.0 + Linux 5.10 lifsea + x86_64`

**重放结果**：

| 观测量 | envA | envB | 一致性 |
|---|---|---|---|
| iso100 N_B 下界 | 29.09812430226496 | 同 | 逐位 |
| iso100 N_B 上界 | 29.09812430426496 | 同 | 逐位 |
| trunc 残差区间 r | [-3365.36, 3142.19] | 同 | 逐位 |
| Dudek 界 | ±5195860.44 | 同 | 逐位 |

判定：**容器重置不构成数值扰因**，浮点/区间算法在双环境下位级可复现。残差区间严格内嵌于 Dudek 界（裕度约 3 个数量级），非紧邻，抗环境抖动。

---

## 四、包A 实跑核验（envB）

**CLI verify 三态**：
| 目标 | ok | 归因 |
|---|---|---|
| iso1000 | true | — |
| trunc | true | — |
| iso100 | **false** | failed 唯一项 = Backlund 异常 |

**failed 唯一项**：`N_B 区间不含唯一整数 —— 拒证`
- 钉档编号：**KI-EXT11-1**
- 语义：区间 [29.09812430226496, 29.09812430426496] 宽度 2e-9，不含整数，Backlund 引理前提不满足 → 合法拒证，非计算错误。

**pytest 尾行**：`41 passed in 1497.81s (0:24:57)`
- 全绿；耗时 24m57s 与 LLT 类长程盲测量级吻合。

---

## 五、双跑闸（决定性判据）

三证书重签时，**进程内同代码连跑两次 → 字节级一致**。
- 证据：`artifacts/witnesses-zeta/run-log-sup01.json`（包A）
- 判定：**去伪确定性已获**——排除"同代码两次跑产生不同见证"的概率性伪证路径。

---

## 六、包 2/3 汇总判定

| 判据 | 结果 |
|---|---|
| 数学字段零改动（44/44） | ✅ |
| 跨环境逐位重放（4/4 观测量） | ✅ |
| CLI 三态行为与 KI-EXT11-1 钉档一致 | ✅ |
| pytest 41 passed | ✅ |
| 双跑字节级确定 | ✅ |
| 变更面 = 披露 + 溯源 + 见证链 | ✅ |

**结论**：包 2/3 通过。v1.0.0→v1.0.1 差异被证明为**纯披露层与见证链升级**，数学内核、跨环境可复现性、拒证行为、确定性重签四项支柱均无退化。

---

## 七、待 3/3 补齐的接口

请包 3/3 覆盖：
1. **v1.0.1 见证链根哈希** 与包A witness_sha256 的对齐（含 psi-trunc 的 zero_source 溯源）
2. **KI-EXT11-1** 钉档在 v1.0.1 的正式条目（触发条件 + 期望输出 + 回归测试锚点）
3. **44 个数学字段的字段名清单或哈希指纹**（便于第三方独立比对）
4. **run-log-sup01.json 的哈希** 及与重签输出的关联证明

包 2/3 已归档，等待 3/3。

——qfa SI1语义轨·20261013T125609Z
