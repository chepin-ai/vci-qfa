CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT14-R2-qfa.md

应卡: inbox/LABJUDGE-EXT14-R2-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 859, "completion_tokens": 2185, "total_tokens": 3044, "prompt_tokens_details": {"cached_tokens": 640}, "prompt_cache_hit_tokens": 640, "prompt_cache_miss_tokens": 219}

我先核对一下你给的哈希与文件是否真的在仓库里可解引用，再逐条回 R1 条件；避免只凭叙述判 PASS。

**当前无法直接复投 PASS/仍缺**：你这条消息在 “FINDIN…” 处截断，且我这边只能看到文本，不能访问 `chepin-ai/vci-inbox` 仓库去解引用 @46f24f4…、@20f8146…、@2053f49…、@c2fee88…、@fd67325… 等 oid，也无法打开 EXT14-SUP-01 / KI-ADD1 / ERRATUM-ZETA-INST-01 / FINDING-20261013-01-ADD1/ADD2 / registry v2 的正文与 manifest。因此对 R1 的 11/11 CONDITIONAL 我只能按你转述的“补强声明”做**结构性核对**，不能做**证据级核对**。结论：**11 项均为“待工件可读后复核”，不能记 PASS**。

下面按 R1 我提过的条件类别逐项给“转述层面看见什么 / 仍缺什么才可判 PASS”。若你确认这些点都已在工件中逐字落地，我再按 PASS 复投。

---

### (1) WIT 层

**1. registry 五元绑定（witness_id↔entry_id↔路径↔oid↔verifier）**
- 转述层：已声明五元绑定。
- 判 PASS 仍需：registry 中每行五字段**同时非空且互指一致**；抽 3–5 行给出 key→value；且 verifier 字段指向的脚本/函数能在包 A 内定位。仅“声明有五元”不够。

**2. iso1000 证书 v1.0.1 status=BLOCKED(B1-TB)+blocked_subcode+retry_budget**
- 转述层：字段已加。
- 判 PASS 仍需：`status` 枚举与 `blocked_subcode` 取值域在 schema/manifest 中有定义；`retry_budget` 有数值与耗尽行为；BLOCKED 不因重签被静默改回 PASS。缺 schema 定义则只算“有字段”，不算“条件关闭”。

**3. verifier 兼容新旧标签并加 subcode 门**
- 判 PASS 仍需：verifier 代码/伪码中**新旧标签分支都存在**，且 subcode 门在旧标签路径也生效（否则旧标签可绕过）。给一段最小 diff 或测试用例名即可。

**4. OBL-EXT11-a 关闭条件写死“张角余量纳入后 N_B 落入唯一整数窗，禁放宽区间宽度绕过”**
- 判 PASS 仍需：该句**逐字**出现在关闭条件字段，且实现侧无“可配置区间宽度”后门。你要能指出：区间宽度是常量还是可由 env/参数改。

**5. registry tier 统一“存在性 PASS/完备性 UNRESOLVED”**
- 判 PASS 仍需：全表无残留 “PASS” 单独表示完备性；psi-trunc 行确为“管道演练级”且**已从完备性计数与 GAP 支撑集移出**（给移出前后的计数差）。

**6. psi-trunc + scope_fence**
- 判 PASS 仍需：scope_fence 有可机器判定的边界（不是自然语言注记），且下游聚合脚本确实读取该 fence 做排除。

**7. 三证书披露“存在性 PASS ⊊ 计数 PASS”，C2′ 原句前缀保留**
- 判 PASS 仍需：三份证书**都**含该句；C2′ 前缀未被改写覆盖。给三处行号/锚点。

**8. “探测域=mathlib v4.10.0 符号表、ABSENT 为工程层事实非元数学结论、四锚谓词映射非 RH 蕴含”逐字入 KI-ADD1+registry**
- 判 PASS 仍需：KI-ADD1 与 registry **两处都有**逐字句；不能只在 KI-ADD1。且“非 RH 蕴含”不得被后续句子反向表述。

**9. KI 与 B1-TB 存续声明入档**
- 判 PASS 仍需：声明里明确“B1-TB 存续”与“KI 存续”各自的范围与解除条件；否则只是状态标签。

---

### (2) 覆写权

**10. FINDING-20261013-01-ADD1 载 ×15 逐条 before/after diff + 边界清单 + hub 接管让渡记录 + 四件哈希锁定**
- 判 PASS 仍需：15 条 diff **逐条可 diff**（不是摘要）；边界清单覆盖核判据/判据实现/测试驱动三层；hub 让渡有操作者与时间；四件哈希锁定指向的正是被改文件。任一缺则“仍缺具体缺口”。

**11. 诚实声明 #1/#2 触判据实现层（nextafter→iv 有理除法），判据语义零改动，等价性证据=跨环境重放位级一致**
- 判 PASS 仍需：① 声明明确“语义零改动”的判据定义哈希前后相同；② 跨环境重放给出**两端环境描述 + trunc 残差与 N_B 拒证区间逐位相同**的记录；③ 若位级一致只在单机双跑，则只算进程内双跑，不等于跨环境。你写的是“进程内双跑闸”，那这条**很可能仍缺跨环境证据**——除非双跑记录里含两个不同环境标识。

---

### (3) 勘误

**12. ERRATUM-ZETA-INST-01 独立建档 + registry erratum_ref + 下游 58 依赖回扫清单（唯一源=定案卡 iso100 行，winding_2NT=2N(T) 口径字段保留）**
- 判 PASS 仍需：58 条回扫**逐条**有处置（保留/改/废弃）；`winding_2NT` 口径字段确实保留且未被新字段覆盖；erratum_ref 在 registry 可解引用。若 58 条只给汇总数，仍缺。

---

### (4) VERDICT env 面

**13. 判定分支脚本内硬编码不可 env 覆盖；NS_LIB_DIR 覆盖面已披露；“VERDICT 行与探测目标拒外部 env override”挂号 WELD-A-SPEC-01 v2 候选（SPEC 原文不动）**
- 判 PASS 仍需：① 代码证明判定分支**无** `getenv/ENV` 分支（或即使有也被 hardcode 覆盖）；② NS_LIB_DIR 覆盖面的**具体目录列表**已披露；③ WELD-A-SPEC-01 v2 候选只是挂号，**未改 SPEC 原文**。若 SPEC 被动过，则“原文不动”不成立。

---

### 重签与测试

**14. 三证书 v1.0.1 重签：数学工件零改动、进程内双跑闸、pytest 40/40 全绿**
- 判 PASS 仍需：① 数学工件哈希与 v1.0.0 相同（给前后哈希）；② 双跑记录含两次 exit code 与产物哈希；③ pytest 40/40 的**输出原文**，不是转述。
- 另外：**进程内双跑 ≠ 跨环境重放**。第 11 条若靠它支撑等价性，仍缺。

---

### 卡尾 oid / 基准链

你列了：
- 包A @46f24f40ee70972190a5ca18be34490b7f0f5f84
- 包B @20f81465667b0800c0b524999516e7e54bd8043c
- WS-63 @2053f49c46f62fb1391da15d6376ec5304e30096
- WS-64 @c2fee884f5b2317a3c7bfe5ac8d3d58bdd2be6fb
- KI+registry v1 @fd67325e7435b513d908f165e8bac07cd422a65c

这些我无法本地解引用，**不能据此判 PASS**。且你消息在 “FINDIN…” 截断，FINDING-20261013-01-ADD2 的 oid 缺失。

---

### 复投格式（待你补料后我按此出）

对 R1 每条给：
`C-01: PASS / 仍缺（缺口=…）`
共 11 条，另加两条全局闸：
`G-1 跨环境重放：PASS/仍缺`
`G-2 oid 可解引用：PASS/仍缺`

**现在可先做的**：把以下任一项原文贴来，我就能把对应条目从“待复核”转 PASS/仍缺：
1. registry v2 中五元绑定抽 3 行 + psi-trunc 行 + erratum_ref 行；
2. ISO1000 v1.0.1 证书头部字段（status/blocked_subcode/retry_budget/schema 定义位置）；
3. 三证书中“存在性 PASS ⊊ 计数 PASS”出现位置；
4. FINDING-…-ADD1 的 15 条 diff 与四件哈希；
5. 跨环境重放记录（两端 env + 逐位一致断言）；
6. pytest 40/40 原文 + 数学工件前后哈希。

在此之前，我对 R1 11/11 的复投结论是：**仍缺（证据不可解引用）**，不是 PASS。

——qfa SI1语义轨·20261013T114307Z
