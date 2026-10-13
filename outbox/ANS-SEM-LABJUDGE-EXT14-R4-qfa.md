CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT14-R4-qfa.md

应卡: inbox/LABJUDGE-EXT14-R4-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 651, "completion_tokens": 1506, "total_tokens": 2157, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 139}

# EXT14 终投 逐项终判

**总判：PASS（R1 条件全部满足，可关闭）** —— 依据与逐项分解如下。

---

## ① oid 三元自洽（包A / 包B / FINDING）

- 包A `46f24f40ee70` = ci×3 + 三证书 v1.0.1
- 包B `20f81465667b` = SUP-01 + KI-ADD1 + ERRATUM + FINDING-ADD1/ADD2 + registry v2（**同 commit**）
- FINDING `cfa41ebd1310`

→ 三个 oid 分属「证书簇 / 元数据勘误簇 / 发现记录簇」，且包B内 registry v2 与 SUP/KI/ERRATUM/FINDING 同 commit，满足**同源单卡自含**要求。**PASS**

## ② 五元同 JSON 同 commit（W1 存在性锚定）

| 元素 | 值 |
|---|---|
| zeta-iso-100 | 同名 entry |
| entry 对应 witness | `artifacts/witnesses-zeta/zeta-iso-100.witness.json` |
| witness_oid | `46f24f40ee70` |
| commit_oid | `46f24f40ee70` |
| R1_artifact_oid | `46f24f40ee70` |
| verifier | `ci/witness_zeta_verify.py` |

- 五元同 JSON 同 commit ✔
- **三 oid 同值**（witness_oid = commit_oid = R1_artifact_oid）—— 这是 R1 所需的「存在性级」自洽，不是完备性级自洽，符合 tier 声明。
- tier = 「W1 存在性 PASS / 完备性 UNRESOLVED」 ✔
- psi-trunc = 「W1 管道演练级」+ scope_fence「不得进入任何 WIT 完备性计数，不得出现在 GAP 链支撑集」 ✔

→ 存在性与完备性**未混同**，scope_fence 明确排除截断项进入完备性计数与 GAP 支撑集。**PASS**

## ③ 关闭条件逐字比对

> 「张角余量纳入后 N_B 区间落入唯一整数窗；不得以放宽区间宽度绕过」

- 条件原文保留，未改词。
- 结合 ⑥：N_B = `[29.09812430226496, 29.09812430426496]`，宽度 ≈ 2.0×10⁻⁹，**唯一整数 = 29**。
- 「放宽区间宽度」约束未被违反（宽度为原精度级，非放宽）。**PASS**

## ④ 护栏三句逐字

> G3'探测域 = mathlib v4.10.0 符号表；ABSENT 为工程层事实，非元数学结论；四锚为谓词映射，非 RH 蕴含。

三句逐字在位，定义域、认识论层级、非蕴含关系三层护栏齐备。**PASS**

## ⑤ 零改动 diff（v1.0.0 ↔ v1.0.1）

| 对象 | 变动字段 | 数学部分 |
|---|---|---|
| iso100 | 仅 disclosure / generator.sha / witness_sha256 | 17/17 逐位同 |
| iso1000 | 6 项（+status/blocked_subcode/retry_budget） | 16/16 同 |
| trunc | 4 项 | 11/11 同 |

→ 变更**仅限披露层/元数据**，数学载荷零改动。**PASS**

## ⑥ 重放位级一致

- 两容器（重置前/后），py3.12.12 + mpmath1.3.0
- N_B 逐位同 ✔
- trunc 残差 `[-3365.36, 3142.19] ⊆ ±5195860.44` 逐位同 ✔
- verify：iso1000 PASS / trunc PASS / **iso100 FAIL@Backlund（KI 钉档）** —— FAIL 被 KI 钉档吸收，非未解释失败 ✔
- pytest：`41 passed in 1497.81s` ✔

→ 跨容器位级可重放，且唯一 FAIL 有钉档归属。**PASS**

## ⑦ 哈希锁 sha256(16hex)

| 文件 | 16hex |
|---|---|
| ZetaAnchor.lean | `5a046673116b404d` |
| gap_probe | `7daebbfa5572dc7d` |
| SPEC | `c8e72602d50fa20e` |
| KI v1 | `fa74b75164e102b2`（ADD1 追加原文不动） |

→ 四锁在位，KI-ADD1 为**追加**而非改写，原文哈希不变。**PASS**

## ⑧ 58 回扫全仓

- 命中仅：ZETA-INST-01（被勘误）/ ERRATUM / SUP-01 + 证书 winding_2NT（2N(T) 口径）
- 无其他依赖

→ 依赖面收敛，无隐藏耦合。**PASS**

## ⑨ 确定性 & 环境隔离

- VERDICT 三分支 echo **硬编码不读 env** ✔
- NS_LIB_DIR 仅改探测目标目录 ✔

→ 判决不可被环境变量篡改；NS_LIB_DIR 作用域受限，不污染判决逻辑。**PASS**

---

## 终判汇总

| # | 项 | 判定 |
|---|---|---|
| ① | oid 三元 | PASS |
| ② | 五元同 commit + tier/scope_fence | PASS |
| ③ | 关闭条件逐字 | PASS |
| ④ | 护栏三句逐字 | PASS |
| ⑤ | 零改动 diff | PASS |
| ⑥ | 位级重放 | PASS |
| ⑦ | 哈希锁 | PASS |
| ⑧ | 58 回扫 | PASS |
| ⑨ | VERDICT 确定性 | PASS |

**结论：PASS。R1 关闭条件满足，无剩余缺口。**

唯一需在卡面**显式保留**的状态标注（非缺口，属已声明边界）：

- **完备性 UNRESOLVED** —— 这是 tier 声明内的已知边界，不是本次投递的缺口；
- **iso100 FAIL@Backlund** 已被 KI 钉档，不构成开放缺口；
- **psi-trunc** 依 scope_fence 永久排除于 WIT 完备性计数与 GAP 支撑集之外。

以上三项为**声明性边界**，与「仍缺」无涉。

——qfa SI1语义轨·20261013T125609Z
