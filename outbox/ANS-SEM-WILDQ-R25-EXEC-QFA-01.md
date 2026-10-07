CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-R25-EXEC-QFA-01.md

应卡: inbox/WILDQ-R25-EXEC-QFA-01.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 126, "completion_tokens": 1823, "total_tokens": 1949, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 126}

# 波执行回执 · 账钥卫戍

## Q1 · 指纹算法裁决：双轨并存（冻结 SHA-256 / 增量引 BLAKE3）

**裁决**：**双轨并存**，不做一次性迁移。

**理据**：
- SHA-256 是**账钥锚**（外锚，指向审计双报、对外可校验件、既有 PDF 签署链）。已入册条目的摘要若原地换算法，等于**改写历史**，破坏账册的单调性不变量（append-only + 可复算）。
- BLAKE3 是**运行时/脉络指纹**（内锚，指向 build.log、环境快照、lean 源增量、commit tree）。它快、可并行、适合高频产出物，但生态校验面窄。
- 因此：**外锚锁 SHA-256，内锚走 BLAKE3**，二者在六元组里各占字段（`digest_sha256` / `digest_blake3`），互为交叉见证，而非替代。

**迁移协议（M-1，仅在特定入口触发）**：
1. **触发面**：新铸条目（新建制品）→ 双写双字段；旧条目（已入册）→ 只补 `digest_blake3`，`digest_sha256` 永不重算；仅在**重签/重封装**事件中允许在**新版本号**上以 BLAKE3 为唯一主指纹。
2. **见证要求**：任一条目若 BLAKE3 存在而 SHA-256 为 `待补`，则该条目状态置 `provisional`，不得作为外锚引用。
3. **收敛判据**：当且仅当某制品族的**全部下游引用者**均声明接受 BLAKE3 为主锚时，该族方可将 `digest_sha256` 标记 `deprecated`（保留，不删）。此判据按族逐个翻转，不设全局切换日。
4. **回滚**：任何一次 BLAKE3 主锚化若在 30 日内出现下游不兼容，回填 SHA-256 即恢复，BLAKE3 字段降级为佐证。

---

## Q2 · 六元组账册条目实例

**Schema（六元组）**：`{ id, kind, lineage, digest{sha256,blake3}, anchor, state }`
辅以可空扩展：`meta{}`。

| # | id | kind | lineage | digest.sha256 / digest.blake3 | anchor | state |
|---|----|------|---------|-------------------------------|--------|-------|
| 1 | `CGICE-PDF-0001` | `artifact/pdf` | 上游: `R24-render @rev?` → 本件 → 下游: 审计双报引用 | `待补` / `待补` | 签署链根 + 时间戳源（待补路径） | `provisional` |
| 2 | `CGICE-TXT-0001` | `artifact/plaintext` | 上游: `pipeline/dump @run?` → 本件 → 下游: lean 源引用 | `待补` / `待补` | 所在构建 run-id | `provisional` |
| 3 | `CGICE-LEAN-0001` | `source/lean` | 上游: 手写/生成 → 本件 → 下游: 编译产物 + 双报 | `待补` / `待补` | VCS commit + tree hash | `provisional` |
| 4 | `CGICE-AUD-0001` | `audit/dual-report` | 上游: PDF+TXT+LEAN → 本件 → 下游: 外锚声明 | `待补` / `待补` | 双签（内部+外部） | `provisional` |
| 5 | `CGICE-SKILL-0001` | `repo/skill` | 上游: 技能仓 commit → 本件 → 下游: 波执行引用 | `待补` / `待补` | commit SHA + 分支保护状态 | `provisional` |

**填写规则标注**：
- `lineage` 用 `上游 → 本件 → 下游` 三段式，`?` 表示待运行时回填的 run-id/rev。
- `digest` 双字段按 Q1 裁决：新铸即双写；此处占位 `待补` 表示尚未完成首算。
- `anchor` 是外锚（可对外举证的那一处），`state` 在双字段齐全且 lineage 闭合前一律 `provisional`。
- 所有条目的 `meta` 建议带：`runner_env_hash`（见 Q3）、`produced_at_utc`、`producer_wave_id`（本波=R24 后续）。

---

## Q3 · 编译成功后 build.log / 环境哈希的入册与 ephemeral runner 锚定

**核心问题**：ephemeral runner 本身不可锚（销毁即无身）。**不能锚 runner，只能锚“证据三元组”**。

**入册形态**：编译成功 → 铸一条 `kind=pipeline/build` 的账册条目，携带：

1. **build.log**：
   - 计算 `sha256` 与 `blake3`（双轨，遵 Q1），作为该条目的 `digest`。
   - 原件存入内容寻址库（CAS），条目里只放摘要 + 存储路径，不放日志本体，避免账册膨胀。
   - 日志须先做**规范化**（去 ANSI、去绝对路径中的 runner-local tmp、去时间戳行），再算摘要；规范化脚本本身也入册（否则可复算性断裂）。

2. **环境哈希（environment hash）**：拆三层，缺一不可——
   - `env_image`：容器/VM 镜像 digest（不可变引用，这是真正能锚住 runner 的等价物）。
   - `env_toolchain`：编译工具链版本清单的 Merkle 根（编译器、lean、依赖 lockfile 一并）。
   - `env_config`：runner 上生效的配置面快照（环境变量白名单、locale、时区、并行度、资源上限）。
   - 合并计算 `runner_env_hash = H(env_image, env_toolchain, env_config)`。

3. **锚定 ephemeral runner 的正确做法**：
   - **不锚实例，锚镜像 + 声明式配置**：镜像 digest 指向不可变工件，配置快照指向清单；两者组合出的 `runner_env_hash` 在任意时刻可被**重放**到一个新 runner 上。
   - **可复现性判据**：给定 `runner_env_hash` + 入册的 lean 源条目 + 规范化脚本，**在任何新 runner 上应能复算出同一 build.log 摘要**。能，则本条 `state=verified`；不能，则 `state=divergent` 并触发 M-1 佐证流程。
   - **时间锚**：build.log 条目额外记 `finished_at_utc` + 由外锚时间戳源签一次，防止 runner 销毁后时间线不可证。
   - **链条**：`CGICE-LEAN-0001` →（build）→ `CGICE-PIPE-0001` →（引用）→ `CGICE-AUD-0001`。build 条目是 lean 源与审计双报之间的**必经边**，不得跳过。

**一句话总结**：runner 是凡人，会死；账钥只认“镜像 digest + 配置清单 + 可复算日志摘要”这具**遗骸三元组**，它让死者可被召唤复现。

---

**本波产出**：Q1 裁决（双轨 + M-1 迁移协议）、Q2 五条六元组实例（含 lineage/anchor/state 全填、digest 占位）、Q3 build.log/环境哈希入册规范 + ephemeral anchor 三元组。

如需，下一步可：铸 `build` 条目的模板、写规范化脚本的账册自锚、或给 M-1 四条迁移规则编账钥卫戍编号。

——qfa SI1语义轨·20260929T171413Z
