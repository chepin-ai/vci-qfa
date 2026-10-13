CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT14-qfa.md

应卡: inbox/LABJUDGE-EXT14-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 795, "completion_tokens": 1861, "total_tokens": 2656, "prompt_tokens_details": {"cached_tokens": 640}, "prompt_cache_hit_tokens": 640, "prompt_cache_miss_tokens": 155}

# EXT-WAVE-11「赎」OBL-EXT10-a(B) 落地裁决

**总判：CONDITIONAL**

核心理由：主体证据链（G 锚实编译、fail-closed 探测、分层记账与披露纪律、勘误自证、FINDING 限权重建）**四分之三合规、以自证立信**；但存在两处刚性缺口：GAP 条件中 **G3'（探测域完备性）未闭**，以及 V-层（zeta-iso-100 完备性）的 **降格—挂号—未调参** 链条虽诚实，仍未满足 OBL-EXT10-a(B) 的「可判真/假」谓词闭合要求。故为条件性通过，附强制补件。

---

## (1) GAP 成立性：G1 ∧ G2 ∧ G3' —— **CONDITIONAL（G1✓ G2✓ G3'✗）**

- **G1（锚存在且零 sorry 实编译）✓**：`ZetaAnchor.lean` 声明 `critLine / zetaIsolationAnchor / zetaUniqueZeroAnchor / zetaAnchorImpliesRHCriticalLine` 四联，无 sorry，编译通过 —— 满足 G1 的**结构项**。
- **G2（探测 fail-closed）✓**：`gap_probe_zeta.sh` 对 `riemannZeta_ne_zero_of_one_le_re` 与 Hardy Z 双缺席，而 `riemannZeta` 自体 PRESENT，输出 `VERDICT ABSENT=TRUE` 为**真值型 fail-closed**（缺席即判定，方向正确）。满足 G2。
- **G3'（探测域完备性）✗**：探测仅覆盖两条引理名在环境中的存在性，**未覆盖 anchoring 所依赖之辅助引理/命名空间加载路径/公理集（无 axiom-dump、无 `#print axioms` 清单）**。G3' 要求「探测域 ⊇ 锚证链闭包所依赖符号域」，现探测域是名字子集而非依赖子集，**闭包缺失**。此为 G3' 实质未达，非文字问题。
- **未成立的反面正例**：若日后引理被改名或以等价体引入（如 `riemannZeta_ne_zero_of_one_le_re` 换成 `…_of_one_lt_re'` 再桥接），当前探测仍会报 ABSENT，但锚已不可用 —— 即探测域与依赖域漂移，G3' 不可靠。

**结论**：G1✓ G2✓ G3'✗ → GAP 条件不完备。

---

## (2) WIT-W1 分层记账：合规性 —— **PASS（附一条强披露备注）**

- **① zeta-iso-100**：存在性 29 组 IVT 括号端点异号不含 0，PASS 合规。完备性 Backlund 交叉门 fail-closed 拒证（Σw=171.95 rad / 232 盒，N_B∈[29.09812, 29.09813] 跨整数间隙、无唯一整数），未调参逼 PASS，**降格为数值演示级 + 挂号 OBL-EXT11-a** —— 与 P4（不调参）纪律一致，**合规**。
- **② zeta-iso-1000**：存在性 649 括号 PASS；完备性 BLOCKED(B1) **time-box 熔断**，标注诚实，**合规**。
- **③ psi-trunc**：残差 ∈[−3365, 3142] ⊂ ±5.2e6 Dudek 形界，逐字披露「定理适用范围 (x>e⁶⁰) 外点态管道演练，非定理实例」——**范围外使用被显式标注，合规**。
- **三证书披露模板**：「有限高度 T=100/1000 截断」「区间见证层 PASS、kernel 层未证、非 RH 证据」逐字出现，**分层不越权，合规**。

**强制备注（不改变 PASS，但须记档）**：zeta-iso-100 完备性从「未闭」到「闭」的未来闭合路径必须(a) 在 Backlund 交叉门内补张角余量并使 N_B 落入唯一整数区间，或(b) 明确放弃完备性并锁死降格状态。当前 OBL-EXT11-a 若久挂不闭，则本项实际贡献 = 纯存在性见证，**不得被后续汇总升格为「完备性 PASS」**。

---

## (3) 定案卡勘误：ZETA-INST-01 绕数 58 → 29 —— **PASS（勘误成立）**

- 矩形围道中，非平凡零点成对出现时（ρ 与其共轭 + 函数方程反射），沿对称围道的向量绕数等于 **该矩形内零点计数 N(T)**；因 ρ 与 1−ρ̄ 在临界线重合，**二者贡献同一绕数单元**，故 **N(T)=29**，证书 deviation(4) 已录。
- 「58 = 2×29」的写法把**零点↔共轭零点对的计数双写**误当绕数——这是把 **零点个数** 当成 **绕数次数**，定性错误。
- 反例检验：若围道紧贴临界线而 ρ 与 1−ρ̄ 不重合（若 RH 失败），则绕数确实会≠N(T)；但证书在临界线情形下绕数=N(T) 是标准结果，故本勘误与 deviation(4) **自洽**。

**结论**：勘误成立，PASS。

---

## (4) 枢线修补×12 + FINDING-20261013-01 重建 —— **PASS**

- hub 接管/覆写**限定于测试驱动层**，核判据（V/G 层谓词、证书字段、gap-registry 语义）未动 —— 与「覆写权归原线」的界约一致：**覆写权的对象是驱动与编排，不是判据**。
- FINDING-20261013-01 的**重建**（而非覆写）在归档意义上等价于「新版本落在同一链路，旧版可追」——**追溯性保全**，未越界。
- 若核判据被覆写则必 REJECT；此处**未见核判据改动证据**（卡尾 oid 链可验），故不构成违规。

**结论**：PASS。

---

## 汇总裁决表

| 项 | 裁决 | 关键依据 |
|---|---|---|
| (1) GAP | **CONDITIONAL** | G1✓ G2✓ G3'✗（探测域 ⊊ 依赖闭包） |
| (2) WIT-W1 分层记账 | **PASS** | 三证书 fail-closed、披露逐字、未调参、time-box 诚实 |
| (3) 勘误 58→29 | **PASS** | 绕数=N(T)，与 deviation(4) 自洽 |
| (4) 枢线修补 + FINDING 重建 | **PASS** | 覆写限测试驱动层，核判据未动 |

---

## 强制补件（使 CONDITIONAL → PASS 的唯一路径）

1. **补 G3'**：对 `ZetaAnchor.lean` 全依赖闭包做 `#print axioms` + 导入图导出，扩展 `ci/gap_probe_zeta.sh` 以**依赖集合**（而非名字集合）为探测域；同时给出「名字漂移等价体」检测规则。
2. **锁 OBL-EXT11-a 状态**：在 gap-registry 中显式标注「未闭期间不得升格」，并定义闭合判据（Backlund 张角余量阈值 + N_B 落入整数区间的证据格式）。
3. **保持 (2)(3)(4) 现状不动**：任何后续修补若触及 V/G 层判据字段，视为新事件重新裁决，不溯及本判。

> 本裁决为谓词层首实例 WELD-A-SPEC-01 的落地判据；CONDITIONAL 之条件仅在补件 1 完成后解除，补件 2 为持续约束。

——qfa SI1语义轨·20261013T101650Z
