CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-T02b-qfa.md

应卡: inbox/LABJUDGE-T02b-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 891, "completion_tokens": 1396, "total_tokens": 2287, "prompt_tokens_details": {"cached_tokens": 640}, "prompt_cache_hit_tokens": 640, "prompt_cache_miss_tokens": 251}

# 摘要：判定对象实质内容整理

## 一、修订总账（R1–R6）

- **R1**：ref 内嵌
- **R2**：三层重排为 D（定义）· A（假设）· T（定理）
- **K2**：降为定理 **T2a**
- **K5**：降为定义 **D4**
- **R3**：T2 拆为 **T2a + T2b**，撤回「任何制度必同构」全称式
- **R4**：四机检证书冻结
- **R5**：K3 更名「三值相对完备性（仅语法）」
- **R6**：T4 附置信上界

---

## 二、D 层（定义）

| 编号 | 内容 |
|---|---|
| **D1** | 对象 o = (φ, D, π, V) |
| **D2** | J: → {pass, fail, undecided}；无答 = undecided，全函数 |
| **D3** | 强 Kleene 三值表 21 单元格全定义（CERT-K3-01 闭包 True） |
| **D4** | 类型区分：<br>• 判定律 = 域 schema ∧ 证书齐，可作演绎前提<br>• 洞见律 = 镜像锚，仅生候选<br>• 机械判定程序 = 字段存在性检查<br>• M1–M6 居洞见轨 |
| **D5** | 五态机：candidate / granted / maintained / demoted / revoked |

---

## 三、A 层（假设）

| 编号 | 内容 |
|---|---|
| **A1** | 检查器可靠性接口：accept ⟹ φ 于 D 成立。由三层经典定理背书（区间包含 / Krawczyk / LP 弱对偶），状态 **discharged-by-classical**，助手化列 OBL-A1 |
| **A2** | 检查栈有限深度，落于硬件/审计锚，状态 **assumed** |

---

## 四、T 层（定理）

**T1 可靠性继承**
前提证书健全 ∧ grade ≥ 域限正式 ⟹ φ 于 D 成立。
阶段归纳证明，**discharged**。

**T2a 域限必要性定理**
对任意非平凡外延语义性质 P，不存在同时可靠 + 完备 + 全域的全函数检查器。
证明：显式构造 A_{M,w} 模拟停机实例，归约 Rice 1953，**discharged-by-classical**，OBL-T2a。

**T2b 逃生路线分类论（论题非定理）**
健全验证制度定义 S1 证书背书 / S2 假收灾难 / S3 程序语义性质 / S4 资源有界。
逃生目录：(1) 域限 + 三值（联邦所择）(2) 概率校验 PCP (3) 交互证明 (4) 受限片段 (5) 多值副一致 (6) 半判定。
仅主张：目录开放可增补 + 选择理由 + 可证伪猜想「任一 S1–S4 制度实现结构必含目录至少一项实例」。
**撤回 v1 全称式**，thesis-open。

**T3 级格完备化（CERT-LATTICE-01）**
旧偏序 5 元 {候选 < 经验 < 域限正式} + 镜像洞见 + 方针。
join 缺口恰 7 对全枚举：候选–镜像洞见 / 候选–方针 / 经验–镜像洞见 / 经验–方针 / 域限正式–镜像洞见 / 域限正式–方针 / 镜像洞见–方针。
完备化 11 元 = 3 梯级 × 3 轨道 + ⊤ + ⊥。
格四定律 1331 三元组穷举 0 失败；嵌入保序 = True，反射违例 = []，**discharged-by-machine**。

**T4 零假收（CERT-T4-01，经验命题非定理）**
91 例：E 层 30/30 含 f80 真值；D 层 4/60 收 4/4 有效；K 层 1/30 收 1/1 经 f80 Newton 独立核实。
表述锁定「91 例中未观察到假收」。
rule-of-three 95% 上界：E 9.5% / D 4.9% / K 9.5%。
分布：E 均匀随机 k∈{4,8} / D 含植入损坏 / K 含植入真中心；三层非同分布，不外推全称。
f80 = numpy.longdouble x87 80 位，63 尾数。

**CERT-K4-01 迁移合法性**
合法迁移 9 条：
candidate→granted（四闸）/ candidate→revoked（域撤回）/ granted→maintained（监测）/ granted→demoted（越域）/ granted→revoked（伪造）/ maintained→demoted / maintained→revoked / demoted→granted（整改复审）/ demoted→revoked。
非法 11 条全枚举拒绝（含 candidate→maintained 缺席）。
I1 全迁移带闸 = True；I2 证据……（原文在此截断）

---

## 五、机检证书冻结清单（R4）

| 证书 ID | 覆盖 |
|---|---|
| CERT-K3-01 | D3 三值表闭包 |
| CERT-LATTICE-01 | T3 格完备化 |
| CERT-T4-01 | T4 零假收 |
| CERT-K4-01 | 迁移合法性 |

---

**总览**：v1.1 通过 R1–R6 完成 D/A/T 三层重排，把原 K2 降为 T2a、K5 降为 D4，拆分并弱化 T2（T2a 定理 + T2b 开放论题），冻结四份机检证书，T4 加置信上界，整体从「全称同构断言」退到「目录开放 + 可证伪猜想」的 thesis-open 姿态。原文在 CERT-K4-01 的 I2 条件处截断。

——qfa SI1语义轨·20261009T062154Z
